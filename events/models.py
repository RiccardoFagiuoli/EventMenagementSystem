from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class Event(models.Model):
    STATUS_CHOICES = [('draft', 'Bozza'), ('published', 'Pubblicato'), ('ongoing', 'In Corso'), ('completed', 'Completato'), ('cancelled', 'Annullato')]
    title = models.CharField(max_length=200, verbose_name='Titolo')
    description = models.TextField(verbose_name='Descrizione')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', verbose_name='Organizzatore')
    location = models.CharField(max_length=255, verbose_name='Luogo')
    start_date = models.DateTimeField(verbose_name='Data e Ora Inizio')
    end_date = models.DateTimeField(verbose_name='Data e Ora Fine')
    max_attendees = models.IntegerField(null=True, blank=True, verbose_name='Numero Massimo Partecipanti')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True, verbose_name='Immagine')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', verbose_name='Stato')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Eliminato il')
    class Meta:
        ordering = ['-start_date']
        permissions = [('can_create_event', 'Può creare eventi'), ('can_edit_own_events', 'Può modificare i propri eventi'), ('can_delete_own_events', 'Può eliminare i propri eventi'), ('can_view_attendees', 'Può visualizzare la lista dei partecipanti')]
    def __str__(self):
        return self.title
    def is_full(self):
        if self.max_attendees is None:
            return False
        return self.eventregistration_set.filter(status='confirmed').count() >= self.max_attendees

    def promote_from_waiting_list(self):
        """"Promuove il primo in lista d'attesa a 'confirmed' """
        # Se l'evento è ancora pieno, non fare nulla
        if self.is_full():
            return None
        # Se l'evento non ha limite di posti, non serve coda
        if self.max_attendees is None:
            return None
        # Cerca il primo in coda
        next_in_line = self.eventregistration_set.filter(status='pending').order_by('registered_at').first()

        # Se trovato qualcuno, promuovi 'confirmed'
        if next_in_line:
            next_in_line.status = 'confirmed'
            next_in_line.save()
            return next_in_line

        return None

    @property
    def get_confirmed_attendees_count(self):
        return self.eventregistration_set.filter(status='confirmed').count()
    def get_pending_attendees_count(self):
        return self.eventregistration_set.filter(status='pending').count()

class EventRegistration(models.Model):
    STATUS_CHOICES = [('pending', 'In Attesa'), ('confirmed', 'Confermato'), ('cancelled', 'Annullato'), ('attended', 'Partecipato')]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-registered_at']
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"
    def get_pending_position(self):
        """Restituisce la posizione nella lista d'attesa"""
        if self.status != 'pending':
            return None

        queryset = EventRegistration.objects.filter(
            event=self.event,
            status='pending'
        ).filter(
            models.Q(registered_at__lt=self.registered_at) |
            models.Q(registered_at=self.registered_at, id__lt=self.id)
        )

        return queryset.count() + 1

class EventAttendance(models.Model):
    registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, related_name='attendance')
    check_in_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.registration.user.username} - {self.registration.event.title} (Partecipato)"


@receiver(pre_save, sender=Event)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Elimina la vecchia immagine quando viene caricata una nuova"""
    if not instance.pk:  # Se è un nuovo evento, esci
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    # Se c'è una nuova immagine e la vecchia esiste ed è diversa
    if new_image and old_image and old_image.name != new_image.name:
        old_image.delete(save=False)  # Elimina il file


@receiver(pre_save, sender=Event)
def handle_image_deletion(sender, instance, **kwargs):
    """Gestisce la cancellazione dell'immagine"""
    if not instance.pk:
        return

    # Se stai usando un campo personalizzato per segnare la cancellazione
    # Puoi passare un attributo temporaneo dall'admin
    if hasattr(instance, '_delete_image') and instance._delete_image:
        if instance.image:
            instance.image.delete(save=False)
            instance.image = None