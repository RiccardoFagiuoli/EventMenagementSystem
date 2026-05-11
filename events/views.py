from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from .models import Event, EventRegistration, EventAttendance
from .forms import EventForm
from users.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime

class EventListView(ListView):
    """ Class-based generic view for listing all published events. """
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.filter(status='published', deleted_at__isnull=True).order_by('start_date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
            # Filtro di ricerca testuale
            query = self.request.GET.get('q')

        # Filtro per nome organizzatore (ricerca parziale)
        organizer_name = self.request.GET.get('organizer_name')
        if organizer_name:
            queryset = queryset.filter(
                Q(organizer__username__icontains=organizer_name)|
                Q(organizer__first_name__icontains=organizer_name) |
                Q(organizer__last_name__icontains=organizer_name)
            )

        # Filtro per data inizio (da data)
        start_date_from = self.request.GET.get('start_date_from')
        if start_date_from:
            try:
                start_date_from = datetime.strptime(start_date_from, '%d/%m/%Y').date()
                queryset = queryset.filter(start_date__date__gte=start_date_from)
            except ValueError:
                pass

        # Filtro per data inizio (a data)
        start_date_to = self.request.GET.get('start_date_to')
        if start_date_to:
            try:
                start_date_to = datetime.strptime(start_date_to, '%d/%m/%Y').date()
                queryset = queryset.filter(start_date__date__lte=start_date_to)
            except ValueError:
                pass

        # Filtro predefinito per data (eventi di oggi)
        date_filter = self.request.GET.get('date_filter')
        if date_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(start_date__date=today)
        elif date_filter == 'upcoming':
            queryset = queryset.filter(start_date__gte=timezone.now())
        elif date_filter == 'past':
            queryset = queryset.filter(start_date__lt=timezone.now())

        # Filtro per organizzatore (selezione esatta dalla tendina)
        organizer_filter = self.request.GET.get('organizer')
        if organizer_filter:
            queryset = queryset.filter(organizer__username=organizer_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events'] = Event.objects.filter(status='published').count()

        # Filtri attuali per il template
        context['current_query'] = self.request.GET.get('q', '')
        context['current_date_filter'] = self.request.GET.get('date_filter', '')
        context['current_organizer'] = self.request.GET.get('organizer', '')
        context['current_organizer_name'] = self.request.GET.get('organizer_name', '')
        context['current_start_date_from'] = self.request.GET.get('start_date_from', '')
        context['current_start_date_to'] = self.request.GET.get('start_date_to', '')

        # Lista di tutti gli organizzatori unici per il filtro a tendina
        organizers_dict = {}
        organizers_data = Event.objects.filter(
            status='published',
            deleted_at__isnull=True
        ).values_list('organizer__username', 'organizer__first_name', 'organizer__last_name')

        for username, first_name, last_name in organizers_data:
            if username not in organizers_dict:  # Rimuove i duplicati manualmente
                full_name = f"{first_name} {last_name}".strip()
                organizers_dict[username] = {
                    'username': username,
                    'full_name': full_name if full_name else username
                }

        # Formatta i nomi degli organizzatori per il template
        context['organizers'] = sorted(organizers_dict.values(), key=lambda x: x['full_name'])

        if self.request.user.is_authenticated:
            user_registrations = EventRegistration.objects.filter(user=self.request.user).values_list('event_id', flat=True)
            context['registered_events'] = user_registrations


            registrations_with_status = EventRegistration.objects.filter(user=self.request.user).values_list('event_id', 'status')
            context['user_registrations_status'] = dict(registrations_with_status)
        return context

class EventDetailView(DetailView):
    """ Class-based generic view for displaying event details. """
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Mostra gli eventi eliminati solo agli organizzatori e admin
        if not self.request.user.is_authenticated or not (self.request.user.is_staff or (hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'organizer')):
            queryset = queryset.filter(deleted_at__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['attendees'] = event.eventregistration_set.filter(status='confirmed').order_by('registered_at')
        context['pending_attendees'] = event.eventregistration_set.filter(status='pending').order_by('registered_at')
        context['can_view_attendees'] = self.request.user == event.organizer or self.request.user.is_staff

        context['pending_count'] = context['pending_attendees'].count()
        context['confirmed_count'] = context['attendees'].count()

        # Calcola se l'evento può essere ripristinato e il tempo rimanente
        if event.deleted_at:
            from datetime import timedelta
            restore_deadline = event.deleted_at + timedelta(days=3)
            time_remaining = restore_deadline - timezone.now()
            context['can_restore'] = time_remaining.total_seconds() > 0

            # Calcola giorni, ore, minuti rimanenti
            total_seconds = max(0, time_remaining.total_seconds())
            days = int(total_seconds // 86400)
            hours = int((total_seconds % 86400) // 3600)
            minutes = int((total_seconds % 3600) // 60)

            context['restore_days'] = days
            context['restore_hours'] = hours
            context['restore_minutes'] = minutes
        else:
            context['can_restore'] = False
            context['restore_days'] = 0
            context['restore_hours'] = 0
            context['restore_minutes'] = 0

        if self.request.user.is_authenticated:
            try:
                registration = EventRegistration.objects.get(event=event, user=self.request.user)
                context['user_registration'] = registration
            except EventRegistration.DoesNotExist:
                context['user_registration'] = None
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    """ Class-based generic view for creating new events. """
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:organizer_events')

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        try:
            profile = self.request.user.profile
            return profile.role == 'organizer' or self.request.user.has_perm('events.can_create_event')
        except UserProfile.DoesNotExist:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            messages.error(request, 'Solo gli organizzatori possono creare eventi.')
            return redirect('events:event_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, 'Evento creato con successo!')
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """ Class-based generic view for updating events. """
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    #success_url = reverse_lazy('events:organizer_events')

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_staff

    def get_success_url(self):
        """Redirige alla pagina di dettaglio dell'evento dopo l'update"""
        return reverse('events:event_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        event = self.get_object()  # Ottieni l'evento originale
        old_image = event.image  # Salva la vecchia immagine

        new_event = form.save(commit=False)

        # GESTISCI CANCELLAZIONE IMMAGINE (checkbox)
        if self.request.POST.get('delete_image') == 'on':
            if old_image:
                old_image.delete()  # Elimina il vecchio file
                new_event.image = None
                messages.info(self.request, 'Immagine rimossa.')

        # GESTISCI SOSTITUZIONE IMMAGINE (se ne carica una nuova)
        elif 'image' in self.request.FILES:
            if old_image and old_image.name != self.request.FILES['image'].name:
                old_image.delete()  # Elimina la vecchia immagine
                messages.info(self.request, 'Immagine sostituita.')

        # Se l'evento è stato eliminato, ripristinalo
        if new_event.deleted_at:
            new_event.deleted_at = None
            messages.success(self.request, 'Evento ripristinato e aggiornato con successo!')
        else:
            messages.success(self.request, 'Evento aggiornato con successo!')

        new_event.save()
        form.save_m2m()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Errore nel modulo. Controlla i dati inseriti.')
        return super().form_invalid(form)

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Class-based generic view for deleting events. """
    model = Event
    template_name = 'events/event_confirm_delete.html'

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        """Questo metodo gestisce le richieste POST (soft delete o hard delete)"""
        event = self.get_object()
        from django.utils import timezone

        if event.deleted_at:
            # Se l'evento è già eliminato, eliminarlo definitivamente dal database
            event_title = event.title
            event.delete()
            messages.success(request, f'Evento "{event_title}" eliminato definitivamente.')
            next_url = reverse('events:organizer_events')
        else:
            # Se l'evento non è eliminato, fare soft delete
            event.deleted_at = timezone.now()
            event.save()
            messages.success(request, 'Evento eliminato con successo! Puoi ripristinarlo entro 3 giorni.')
            next_url = reverse('events:event_detail', kwargs={'pk': event.pk})

        return redirect(next_url)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


def event_register(request, pk):
    """ View for registering a user to an event. """
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati per registrarsi.')
        return redirect('users:login')
    event = get_object_or_404(Event, pk=pk, status='published')

    # Controlla se l'utente è il creatore dell'evento
    if request.user == event.organizer:
        messages.error(request, 'Non puoi iscriverti al tuo stesso evento.')
        return redirect('events:event_detail', pk=pk)

    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
        if registration.status == 'cancelled':
            # Ri-iscrizione da cancellato
            if event.is_full():
                # Evento pieno → lista d'attesa
                registration.status = 'pending'
                registration.save()
                messages.warning(request, 'Evento al completo. Sei stato aggiunto alla lista d\'attesa.')
            else:
                # Evento con posti → confermato
                registration.status = 'confirmed'
                registration.save()
                messages.success(request, 'Iscrizione completata!')
        elif registration.status == 'pending':
            messages.warning(request, 'Sei già in lista d\'attesa per questo evento.')
        else:  # status == 'confirmed'
            messages.warning(request, 'Sei già registrato a questo evento.')

    except EventRegistration.DoesNotExist:
        # Nuova registrazione
        if event.is_full():
            # Evento pieno → lista d'attesa
            registration = EventRegistration.objects.create(
                event=event,
                user=request.user,
                status='pending'
            )
            messages.warning(request, 'Evento al completo. Sei stato aggiunto alla lista d\'attesa.')
        else:
            # Evento con posti → confermato
            registration = EventRegistration.objects.create(
                event=event,
                user=request.user,
                status='confirmed'
            )
            messages.success(request, 'Registrazione completata!')

    return redirect('events:event_detail', pk=pk)


@login_required
def event_unregister_confirm(request, pk):
    """Pagina di conferma per la disiscrizione da un evento"""
    event = get_object_or_404(Event, pk=pk)

    # Verifica che l'utente sia effettivamente registrato all'evento
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
    except EventRegistration.DoesNotExist:
        messages.error(request, 'Non sei registrato a questo evento.')
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        # Conferma la disiscrizione
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, f'Sei stato disiscritto dall\'evento "{event.title}" con successo.')

        # PROMUOVI DALLA LISTA D'ATTESA
        promoted = event.promote_from_waiting_list()

        if promoted:
            promoted_name = promoted.user.get_full_name() or promoted.user.username
            messages.info(request, f'{promoted_name} è stato promosso dalla lista d\'attesa!')

        return redirect('events:event_detail', pk=pk)

    # GET: mostra la pagina di conferma
    context = {
        'event': event,
        'registration': registration,
    }
    return render(request, 'events/confirm_unregister.html', context)

def event_unregister(request, pk):
    """ View for unregistering a user from an event. """
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati.')
        return redirect('users:login')
    event = get_object_or_404(Event, pk=pk)
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, 'Cancellazione registrazione completata!')
        # PROMUOVI DALLA LISTA D'ATTESA
        promoted = event.promote_from_waiting_list()

        # Messaggio di conferma promozione
        if promoted:
            promoted_name = promoted.user.get_full_name() or promoted.user.username
    except EventRegistration.DoesNotExist:
        messages.error(request, 'Non sei registrato a questo evento.')
    return redirect('events:event_detail', pk=pk)


def user_registrations(request):
    """ View to display user's event registrations with filters and pagination. """
    if not request.user.is_authenticated:
        return redirect('users:login')

    # Recupera parametri di filtro
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', 'all')

    # Query base
    queryset = EventRegistration.objects.filter(user=request.user).select_related('event')

    # Filtro per stato
    if status_filter != 'all':
        queryset = queryset.filter(status=status_filter)

    # Filtro per data
    now = timezone.now()
    if date_filter == 'upcoming':
        queryset = queryset.filter(event__start_date__gte=now)
    elif date_filter == 'past':
        queryset = queryset.filter(event__end_date__lt=now)
    # 'all' = nessun filtro

    # Ordina per data evento (più recenti prima)
    queryset = queryset.order_by('status', '-event__start_date')

    # Calcola statistiche per i gruppi (sul queryset totale senza filtri)
    all_registrations = EventRegistration.objects.filter(user=request.user)

    # Paginazione
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 10)  # 10 registrazioni per pagina
    page_number = request.GET.get('page')
    registrations_page = paginator.get_page(page_number)

    has_confirmed = any(r.status == 'confirmed' for r in registrations_page)
    has_pending = any(r.status == 'pending' for r in registrations_page)
    has_cancelled = any(r.status == 'cancelled' for r in registrations_page)

    context = {
        'registrations': registrations_page,
        'paginator': paginator,
        'title': 'Le mie registrazioni',
        'has_confirmed': has_confirmed,
        'has_pending': has_pending,
        'has_cancelled': has_cancelled,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'events/user_registrations.html', context)

def organizer_events(request):
    """ View to display organizer's events. """
    if not request.user.is_authenticated:
        return redirect('users:login')
    try:
        profile = request.user.profile
        is_organizer = profile.role == 'organizer'
    except UserProfile.DoesNotExist:
        is_organizer = False
    
    is_admin = request.user.is_staff
    
    if not is_organizer and not is_admin:
        messages.error(request, 'Accesso negato. Solo gli organizzatori possono visualizzare questa pagina.')
        return redirect('events:event_list')

    # Recupera parametri di filtro
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    show_deleted = request.GET.get('show_deleted', '') == 'true'

    # Admin vede tutti gli eventi, gli organizzatori vedono solo i loro
    if is_admin:
        queryset = Event.objects.all().order_by('start_date')
    else:
        queryset = Event.objects.filter(organizer=request.user).order_by('start_date')

    # Filtro per elementi eliminati
    if not show_deleted:
        queryset = queryset.filter(deleted_at__isnull=True)

    # Filtro ricerca
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Filtro per stato
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Filtro per data
    today = timezone.now().date()
    now = timezone.now()
    if date_filter == 'upcoming':
        queryset = queryset.filter(start_date__date__gte=today)
    elif date_filter == 'past':
        queryset = queryset.filter(end_date__date__lt=today)
    elif date_filter == 'ongoing':
        queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
    # 'all' o vuoto = nessun filtro

    # Ordinamento (diverso per admin e organizzatore)
    if is_admin:
        queryset = queryset.order_by('-start_date')  # Admin: più recenti prima
    else:
        if date_filter == 'past':
            queryset = queryset.order_by('-start_date')  # Passati: più recenti prima
        else:
            queryset = queryset.order_by('start_date')  # Prossimi: più vicini prima

    # Aggiungi proprietà can_restore
    for event in queryset:
        if event.deleted_at:
            event.can_restore = (timezone.now() - event.deleted_at).days < 3
        else:
            event.can_restore = False

    # Paginazione
    paginator = Paginator(queryset, 10)  # 12 eventi per pagina
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)
    context = {
        'events': events_page,
        'paginator': paginator,
        'title': 'I Miei Eventi',
        'is_admin': is_admin,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'show_deleted': show_deleted,
        'status_choices': Event._meta.get_field('status').choices,
    }
    return render(request, 'events/organizer_events.html', context)

def event_restore(request, pk):
    """ View to restore a deleted event. """
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati.')
        return redirect('users:login')

    event = get_object_or_404(Event, pk=pk)

    # Permetti sia all'organizzatore che agli admin
    if not (request.user == event.organizer or request.user.is_staff):
        messages.error(request, 'Non hai i permessi per ripristinare questo evento.')
        return redirect('events:organizer_events')

    if event.deleted_at:
        from django.utils import timezone
        if (timezone.now() - event.deleted_at).days < 3:
            event.deleted_at = None
            event.save()
            messages.success(request, f'Evento "{event.title}" ripristinato con successo!')
        else:
            messages.error(request, 'Non è possibile ripristinare eventi eliminati da più di 3 giorni.')
    else:
        messages.warning(request, 'L\'evento non è eliminato.')

    return redirect('events:event_detail', pk=pk)

@login_required
def admin_unregister_confirm(request, event_id, registration_id):
    """Pagina di conferma per disiscrivere un utente da un evento (solo admin/organizzatore)"""
    event = get_object_or_404(Event, pk=event_id)

    # Permetti solo all'admin o all'organizzatore dell'evento
    if not (request.user.is_staff or request.user == event.organizer):
        messages.error(request, 'Accesso negato. Solo gli admin e l\'organizzatore possono eseguire questa azione.')
        return redirect('events:event_list')

    registration = get_object_or_404(EventRegistration, pk=registration_id, event=event)
    user_to_unregister = registration.user

    if request.method == 'POST':
        # Conferma la disiscrizione
        user_name = user_to_unregister.get_full_name() or user_to_unregister.username
        registration.delete()
        messages.success(request, f'✅ Utente {user_name} disiscritto dall\'evento "{event.title}" con successo.')

        # PROMUOVI DALLA LISTA D'ATTESA
        promoted = event.promote_from_waiting_list()

        # Messaggio di conferma promozione
        if promoted:
            promoted_name = promoted.user.get_full_name() or promoted.user.username
            messages.success(request,
                             f'🎉 Un posto si è liberato! {promoted_name} è stato promosso dalla lista d\'attesa.')

        return redirect('events:event_detail', pk=event_id)

    # GET: mostra la pagina di conferma
    context = {
        'event': event,
        'registration': registration,
        'user_to_unregister': user_to_unregister,
        'is_admin_action': True,
    }
    return render(request, 'events/confirm_unregister.html', context)

def admin_unregister_user(request, event_id, registration_id):
     """ View to unregister a user from an event (admin and organizer only). Promuove il primo in coda """
     if not request.user.is_authenticated:
         messages.error(request, 'È necessario essere loggati.')
         return redirect('users:login')

     event = get_object_or_404(Event, pk=event_id)

     # Permetti solo all'admin o all'organizzatore dell'evento
     if not (request.user.is_staff or request.user == event.organizer):
         messages.error(request, 'Accesso negato. Solo gli admin e l\'organizzatore possono eseguire questa azione.')
         return redirect('events:event_list')

     registration = get_object_or_404(EventRegistration, pk=registration_id, event=event)

     user_name = registration.user.username
     registration.delete()
     messages.success(request, f'Utente {user_name} discritto dall\'evento {event.title}.')

     # PROMUOVI DALLA LISTA D'ATTESA
     promoted = event.promote_from_waiting_list()

     # Messaggio di conferma promozione
     if promoted:
         promoted_name = promoted.user.get_full_name() or promoted.user.username
         messages.warning(request,f'🎉 Un posto si è liberato! {promoted_name} è stato promosso dalla lista d\'attesa.')
     return redirect('events:event_detail', pk=event_id)


@login_required
def admin_register_confirm(request, pk, registration_pk):
    """Pagina di conferma per iscrivere un utente dalla lista d'attesa (solo admin/organizzatore)"""
    event = get_object_or_404(Event, pk=pk, status='published')
    registration = get_object_or_404(EventRegistration, pk=registration_pk, event=event)

    # Controllo permessi
    if not (request.user.is_staff or request.user == event.organizer):
        messages.error(request, 'Non hai i permessi per questa azione.')
        return redirect('events:event_detail', pk=pk)

    # Verifica che l'utente sia effettivamente in lista d'attesa
    if registration.status != 'pending':
        messages.warning(request, 'Questo utente non è in lista d\'attesa.')
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        # Conferma l'iscrizione
        registration.status = 'confirmed'
        registration.save()

        user_name = registration.user.get_full_name() or registration.user.username
        messages.success(request, f'✅ {user_name} è stato iscritto all\'evento "{event.title}" con successo!')

        return redirect('events:event_detail', pk=pk)

    # GET: mostra la pagina di conferma
    context = {
        'event': event,
        'registration': registration,
        'user_to_register': registration.user,
        'is_admin_register': True,
    }
    return render(request, 'events/confirm_register.html', context)

def admin_register_user(request, pk, registration_pk):
    """View per admin per confermare utente dalla lista d'attesa"""
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati.')
        return redirect('users:login')

    event = get_object_or_404(Event, pk=pk, status='published')
    registration = get_object_or_404(EventRegistration, pk=registration_pk, event=event)

    # Controllo permessi
    if not (request.user.is_staff or request.user == event.organizer):
        messages.error(request, 'Non hai i permessi per questa azione.')
        return redirect('events:event_detail', pk=pk)

    # Conferma dalla lista d'attesa
    if registration.status == 'pending':
        registration.status = 'confirmed'
        registration.save()
        messages.success(request, f'{registration.user.username} è stato iscritto all\'evento!')
    else:
        messages.warning(request, 'Questo utente non è in lista d\'attesa.')
    return redirect('events:event_detail', pk=pk)

def deleted_events(request):
    """ View to display all deleted events (admin only). """
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati.')
        return redirect('users:login')

    if not request.user.is_staff:
        messages.error(request, 'Accesso negato. Solo gli admin possono visualizzare questa pagina.')
        return redirect('events:event_list')

    # Mostra tutti gli eventi eliminati (soft deleted)
    deleted_events_list = Event.objects.filter(deleted_at__isnull=False).order_by('-deleted_at')

    from django.utils import timezone
    from datetime import timedelta

    # Calcola il tempo rimanente per ogni evento
    for event in deleted_events_list:
        restore_deadline = event.deleted_at + timedelta(days=3)
        time_remaining = restore_deadline - timezone.now()
        event.can_restore = time_remaining.total_seconds() > 0

        # Calcola giorni, ore, minuti rimanenti
        total_seconds = max(0, time_remaining.total_seconds())
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)

        event.restore_days = days
        event.restore_hours = hours
        event.restore_minutes = minutes

    context = {'deleted_events': deleted_events_list, 'title': 'Eventi Eliminati'}
    return render(request, 'events/deleted_events.html', context)

@login_required
def calendar_view(request):
    """ View to display user's event calendar. """
    # Impedisce gli admin di accedere (non possono iscriversi agli eventi)
    if request.user.is_staff:
        messages.error(request, 'Gli admin non possono visualizzare il calendario.')
        return redirect('home')

    return render(request, 'events/calendar.html', {'title': 'Calendario'})

@login_required
def calendar_events(request):
    """ API endpoint to get user's registered events in JSON format. """
    # Impedisce gli admin di accedere
    if request.user.is_staff:
        return JsonResponse([], safe=False)

    events = []

    # 1. Eventi a cui l'utente è registrato
    registrations = EventRegistration.objects.filter(
        user=request.user,
        status='confirmed'
    ).select_related('event')

    for registration in registrations:
        event = registration.event
        # Salta gli eventi eliminati
        if event.deleted_at:
            continue

        events.append({
            'title': f'📝 {event.title}',  # Icona per eventi registrati
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'backgroundColor': 'white',
            'borderColor': '#667eea',
            'textColor': 'black',
            'display': 'block',
            'classNames':['custom-border-registered'],
            'url': reverse('events:event_detail', kwargs={'pk': event.id}),
            'extendedProps': {
                'location': event.location,
            }
        })

    # Eventi creati dall'utente (organizzatore)
    try:
        if request.user.profile.role == 'organizer':
            user_events = Event.objects.filter(
                organizer=request.user,
                deleted_at__isnull=True,  # Solo eventi non eliminati
                status='published'
            )

            for event in user_events:
                events.append({
                    'title': f'🎯 {event.title}',  # Icona per eventi creati
                    'start': event.start_date.isoformat(),
                    'end': event.end_date.isoformat(),
                    'backgroundColor': 'white',
                    'borderColor': '#764ba2',
                    'textColor': '#764ba2',
                    'display': 'block',
                    'classNames':['custom-border-organized'],
                    'url': reverse('events:event_detail', kwargs={'pk': event.id}),
                    'extendedProps': {
                        'location': event.location,
                    }
                })
    except UserProfile.DoesNotExist:
        pass

    return JsonResponse(events, safe=False)