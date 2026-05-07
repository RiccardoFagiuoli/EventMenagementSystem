from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import UserProfile

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
