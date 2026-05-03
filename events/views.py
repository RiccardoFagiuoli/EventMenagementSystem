from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Event, EventRegistration, EventAttendance
from users.models import UserProfile

class EventListView(ListView):
    """ Class-based generic view for listing all published events. """
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.filter(status='published').order_by('-start_date')
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
    template_name = 'events/event_form.html'
    fields = ['title', 'description', 'location', 'start_date', 'end_date', 'max_attendees', 'image', 'status']
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
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
    template_name = 'events/event_form.html'
    fields = ['title', 'description', 'location', 'start_date', 'end_date', 'max_attendees', 'image', 'status']
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.has_perm('events.can_edit_own_events')

    def form_valid(self, form):
        messages.success(self.request, 'Evento aggiornato con successo!')
        return super().form_valid(form)

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """ Class-based generic view for deleting events. """
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:event_list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.has_perm('events.can_delete_own_events')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Evento eliminato con successo!')
        return super().delete(request, *args, **kwargs)

def event_register(request, pk):
    """ View for registering a user to an event. """
    if not request.user.is_authenticated:
        messages.error(request, 'È necessario essere loggati per registrarsi.')
        return redirect('login')
    event = get_object_or_404(Event, pk=pk, status='published')
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
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
        return redirect('login')
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
        return redirect('login')
    registrations = EventRegistration.objects.filter(user=request.user).order_by('-registered_at')
    context = {'registrations': registrations, 'title': 'Le mie registrazioni'}
    return render(request, 'events/user_registrations.html', context)

def organizer_events(request):
    """ View to display organizer's events. """
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        profile = request.user.profile
        if profile.role != 'organizer' and not request.user.has_perm('events.can_create_event'):
            messages.error(request, 'Accesso negato. Solo gli organizzatori possono visualizzare questa pagina.')
            return redirect('events:event_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profilo utente non trovato.')
        return redirect('events:event_list')
    events = Event.objects.filter(organizer=request.user).order_by('-start_date')
    context = {'events': events, 'title': 'I miei eventi'}
    return render(request, 'events/organizer_events.html', context)
