from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Event, EventRegistration, EventAttendance
from .forms import EventForm
from users.models import UserProfile

class EventListView(ListView):
    """ Class-based generic view for listing all published events. """
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.filter(status='published', deleted_at__isnull=True).order_by('-start_date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_events'] = Event.objects.filter(status='published').count()
        if self.request.user.is_authenticated:
            user_registrations = EventRegistration.objects.filter(user=self.request.user).values_list('event_id', flat=True)
            context['registered_events'] = user_registrations
        return context

class EventDetailView(DetailView):
    """ Class-based generic view for displaying event details. """
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'profile') or self.request.user.profile.role != 'organizer':
            queryset = queryset.filter(deleted_at__isnull=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['attendees'] = event.eventregistration_set.filter(status='confirmed')
        context['can_view_attendees'] = self.request.user == event.organizer or self.request.user.has_perm('events.can_view_attendees')
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
    success_url = reverse_lazy('events:organizer_events')

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Evento aggiornato con successo!')
        return super().form_valid(form)

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Class-based generic view for deleting events. """
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:organizer_events')

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        """Questo metodo gestisce le richieste POST (soft delete)"""
        event = self.get_object()
        from django.utils import timezone
        event.deleted_at = timezone.now()
        event.save()
        messages.success(request, 'Evento eliminato con successo! Puoi ripristinarlo entro 3 giorni.')
        return redirect(self.success_url)

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
            if event.is_full():
                messages.error(request, 'L\'evento è al completo.')
            else:
                registration.status = 'confirmed' if not event.is_full() else 'pending'
                registration.save()
                messages.success(request, 'Iscrizione completata!')
        else:
            messages.warning(request, 'Sei già registrato a questo evento.')
    except EventRegistration.DoesNotExist:
        if event.is_full():
            messages.error(request, 'L\'evento è al completo.')
        else:
            registration = EventRegistration.objects.create(event=event, user=request.user, status='confirmed' if not event.is_full() else 'pending')
            messages.success(request, 'Registrazione completata!')
    return redirect('events:event_detail', pk=pk)

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
    except EventRegistration.DoesNotExist:
        messages.error(request, 'Non sei registrato a questo evento.')
    return redirect('events:event_detail', pk=pk)

def user_registrations(request):
    """ View to display user's event registrations. """
    if not request.user.is_authenticated:
        return redirect('users:login')
    registrations = EventRegistration.objects.filter(user=request.user).order_by('-registered_at')
    context = {'registrations': registrations, 'title': 'Le mie registrazioni'}
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
        messages.error(request, 'Accesso negato. Solo gli organizzatori e gli admin possono visualizzare questa pagina.')
        return redirect('events:event_list')
    
    # Admin vede tutti gli eventi, gli organizzatori vedono solo i loro
    if is_admin:
        events = Event.objects.all().order_by('-start_date')
    else:
        events = Event.objects.filter(organizer=request.user).order_by('-start_date')
    
    from django.utils import timezone
    for event in events:
        if event.deleted_at:
            event.can_restore = (timezone.now() - event.deleted_at).days < 3
        else:
            event.can_restore = False
    context = {'events': events, 'title': 'I miei eventi', 'is_admin': is_admin}
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

    return redirect('events:organizer_events')

def admin_unregister_user(request, event_id, registration_id):
    """ View to unregister a user from an event (admin only). """
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Accesso negato. Solo gli admin possono eseguire questa azione.')
        return redirect('events:event_list')
    
    event = get_object_or_404(Event, pk=event_id)
    registration = get_object_or_404(EventRegistration, pk=registration_id, event=event)
    
    user_name = registration.user.username
    registration.delete()
    messages.success(request, f'Utente {user_name} discritto dall\'evento {event.title}.')
    return redirect('events:event_detail', pk=event_id)

