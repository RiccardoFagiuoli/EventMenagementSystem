from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import User
from events.models import Event, EventRegistration

def home(request):
    """ Home page view """

    # Contatori base
    total_events = Event.objects.filter(deleted_at__isnull=True).count()
    total_users = User.objects.count()
    upcoming_events_count = Event.objects.filter(
        start_date__date=timezone.now().date(),
        start_date__gte=timezone.now(),
        deleted_at__isnull=True
    ).count()

    # Tentativo di contare gli organizzatori (potrebbe fallire se non esiste)
    try:
        from users.models import UserProfile
        total_organizers = UserProfile.objects.filter(role='organizer').count()
    except:
        total_organizers = 0

    # Contatori specifici per l'utente loggato
    if request.user.is_authenticated:
        # Numero di eventi creati dall'utente (se è organizzatore)
        total_organizer_events = Event.objects.filter(
            organizer=request.user,
            deleted_at__isnull=True
        ).count()

        # Numero di iscrizioni dell'utente
        total_subscriptions = EventRegistration.objects.filter(
            user=request.user
        ).count()
    else:
        total_organizer_events = 0
        total_subscriptions = 0

    context = {
        'total_events': total_events,
        'total_users': total_users,
        'total_organizer_events': total_organizer_events,
        'total_subscriptions': total_subscriptions,
        'total_attendees': EventRegistration.objects.filter(status='confirmed').count(),
        'upcoming_events_count': upcoming_events_count,
        'total_organizers': total_organizers,
        'featured_events': Event.objects.filter(deleted_at__isnull=True).order_by('-created_at')[:3],
        'upcoming_events': Event.objects.filter(
            start_date__gte=timezone.now(),
            deleted_at__isnull=True
        ).order_by('start_date')[:5],
        'now': timezone.now(),
    }

    return render(request, 'home.html', context)