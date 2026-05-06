from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Event(models.Model):
    STATUS_CHOICES = [('draft', 'Bozza'), ('published', 'Pubblicato'), ('ongoing', 'In Corso'), ('completed', 'Completato'), ('cancelled', 'Annullato')]
    title = models.CharField(max_length=200, verbose_name='Titolo')
    description = models.TextField(verbose_name='Descrizione')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events', verbose_name='Organizzatore')
    location = models.CharField(max_length=255, verbose_name='Luogo')
    start_date = models.DateTimeField(verbose_name='Data e Ora Inizio')
    end_date = models.DateTimeField(verbose_name='Data e Ora Fine')
    max_attendees = models.IntegerField(blank=True, verbose_name='Numero Massimo Partecipanti')
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

    @property
    def get_confirmed_attendees_count(self):
        return self.eventregistration_set.filter(status='confirmed').count()

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

class EventAttendance(models.Model):
    registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, related_name='attendance')
    check_in_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.registration.user.username} - {self.registration.event.title} (Partecipato)"
