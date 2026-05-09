from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import UserProfile
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

def is_admin(user):
    return user.is_authenticated and user.is_staff

def register(request):
    """ View for user registration. """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'attendee')
        phone = request.POST.get('phone')

        if password != password_confirm:
            messages.error(request, 'Le password non corrispondono.')
            return redirect('users:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Questo username è già stato utilizzato.')
            return redirect('users:register')

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        group = Group.objects.get(name=role.capitalize())
        user.groups.add(group)
        UserProfile.objects.create(user=user, role=role, phone_number=phone)
        messages.success(request, 'Registrazione completata! Accedi adesso.')
        return redirect('users:login')

    return render(request, 'users/register.html')

def user_login(request):
    """ View for user login. """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Benvenuto {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Username o password non validi.')
    return render(request, 'users/login.html')

@login_required
@require_http_methods(["POST"])
def user_logout(request):
    """ View for user logout. """
    logout(request)
    messages.success(request, 'Logout completato!')
    return redirect('home')

@login_required
def profile(request):
    """ View for displaying and editing user profile. """
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        user_profile.bio = request.POST.get('bio', user_profile.bio)
        user_profile.phone_number = request.POST.get('phone_number', user_profile.phone_number)
        user_profile.save()
        messages.success(request, 'Profilo aggiornato con successo!')
        return redirect('users:profile')

    context = {'profile': user_profile}
    return render(request, 'users/profile.html', context)


@user_passes_test(is_admin)
def user_list(request):
    """
    Vista per la lista utenti (solo admin)
    """
    # Filtri
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    # Query base
    users = User.objects.select_related('profile').all()

    # Applica filtri
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if role_filter:
        if role_filter == 'organizer':
            users = users.filter(profile__role='organizer')
        elif role_filter == 'attendee':
            users = users.filter(profile__role='attendee')
        elif role_filter == 'admin':
            users = users.filter(is_staff=True)

    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)

    # Ordina per data di creazione (più recenti prima)
    users = users.order_by('-date_joined')

    # Aggiungi conteggio eventi per organizzatori
    for user in users:
        if hasattr(user, 'profile') and user.profile.role == 'organizer':
            user.event_count = user.organized_events.count()
        else:
            user.event_count = 0

    # Paginazione
    paginator = Paginator(users, 20)  # 20 utenti per pagina
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiche per i filtri
    stats = {
        'total': User.objects.count(),
        'organizers': User.objects.filter(profile__role='organizer').count(),
        'attendees': User.objects.filter(profile__role='attendee').count(),
        'admins': User.objects.filter(is_staff=True).count(),
        'active': User.objects.filter(is_active=True).count(),
        'inactive': User.objects.filter(is_active=False).count(),
    }

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'stats': stats,
    }

    return render(request, 'users/user_list.html', context)


@user_passes_test(is_admin)
def user_detail(request, user_id):
    """
    Vista per il dettaglio di un singolo utente
    """
    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)

    # Eventi creati (se è organizzatore)
    events_organized = user.organized_events.all() if hasattr(user, 'organized_events') else []

    # Eventi a cui partecipa (escludendo status cancelled)
    try:
        events_attending = user.event_registrations.filter(
            ~Q(status='cancelled')
        ).select_related('event', 'event__organizer')
    except:
        events_attending = []

    context = {
        'user_detail': user,
        'events_organized': events_organized,
        'events_attending': events_attending,
    }

    return render(request, 'users/user_detail.html', context)


@user_passes_test(is_admin)
def organizer_list(request):
    """
    Vista per la lista degli organizzatori (solo admin)
    """
    # Filtri
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'events_count')  # Default: ordina per numero eventi

    # Query base - solo utenti con ruolo organizer
    organizers = User.objects.filter(
        profile__role='organizer'
    ).select_related('profile').prefetch_related('organized_events')

    # Applica filtri di ricerca
    if search_query:
        organizers = organizers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # Aggiungi conteggio eventi e altre statistiche
    for organizer in organizers:
        organizer.events_count = organizer.organized_events.count()

        # Usa 'eventregistration' invece di 'registrations'
        organizer.total_participants = organizer.organized_events.aggregate(
            total=Count('eventregistration')  # Cambiato da 'registrations' a 'eventregistration'
        )['total'] or 0

        organizer.avg_participants = organizer.organized_events.aggregate(
            avg=Avg('eventregistration')  # Cambiato da 'registrations' a 'eventregistration'
        )['avg'] or 0

        organizer.upcoming_events = organizer.organized_events.filter(
            start_date__gte=timezone.now()  # Usa start_date invece di date
        ).count()

    # Ordina
    if sort_by == 'events_count':
        organizers = sorted(organizers, key=lambda x: x.events_count, reverse=True)
    elif sort_by == 'name':
        organizers = sorted(organizers, key=lambda x: x.username.lower())
    elif sort_by == 'date_joined':
        organizers = organizers.order_by('-date_joined')
    elif sort_by == 'total_participants':
        organizers = sorted(organizers, key=lambda x: x.total_participants, reverse=True)

    # Paginazione
    paginator = Paginator(organizers, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistiche
    total_organizers = User.objects.filter(profile__role='organizer').count()
    active_organizers = User.objects.filter(profile__role='organizer', is_active=True).count()
    inactive_organizers = User.objects.filter(profile__role='organizer', is_active=False).count()
    total_events = sum(o.events_count for o in organizers)
    total_participants = sum(o.total_participants for o in organizers)

    # Trova il top organizer
    top_organizer_name = 'N/A'
    if organizers:
        top_organizer = max(organizers, key=lambda x: x.events_count)
        top_organizer_name = top_organizer.get_full_name() or top_organizer.username

    stats = {
        'total_organizers': total_organizers,
        'active_organizers': active_organizers,
        'inactive_organizers': inactive_organizers,
        'total_events': total_events,
        'total_participants': total_participants,
        'top_organizer': top_organizer_name,
    }

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'stats': stats,
    }

    return render(request, 'users/organizer_list.html', context)