#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventmenagementsystem.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import UserProfile
from events.models import Event, EventRegistration, EventAttendance

# Clear existing data
User.objects.all().delete()
Event.objects.all().delete()
Group.objects.all().delete()

# Create groups with permissions
attendee_group, _ = Group.objects.get_or_create(name='Attendee')
organizer_group, _ = Group.objects.get_or_create(name='Organizer')

# Get content types
event_ct = ContentType.objects.get_for_model(Event)

# Get or create permissions
can_create_event_perm, _ = Permission.objects.get_or_create(
    codename='can_create_event',
    content_type=event_ct,
    defaults={'name': 'Can create events'}
)
can_edit_own_events_perm, _ = Permission.objects.get_or_create(
    codename='can_edit_own_events',
    content_type=event_ct,
    defaults={'name': 'Can edit own events'}
)
can_delete_own_events_perm, _ = Permission.objects.get_or_create(
    codename='can_delete_own_events',
    content_type=event_ct,
    defaults={'name': 'Can delete own events'}
)
can_view_attendees_perm, _ = Permission.objects.get_or_create(
    codename='can_view_attendees',
    content_type=event_ct,
    defaults={'name': 'Can view attendees list'}
)

# Assign permissions to Attendee group (minimal permissions)
attendee_group.permissions.set([])

# Assign permissions to Organizer group (all permissions)
organizer_group.permissions.set([
    can_create_event_perm,
    can_edit_own_events_perm,
    can_delete_own_events_perm,
    can_view_attendees_perm
])

# Create sample users
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@eventmgmt.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()

# Create organizer users
organizer1, created = User.objects.get_or_create(
    username='marco_rossi',
    defaults={
        'email': 'marco.rossi@event.com',
        'first_name': 'Marco',
        'last_name': 'Rossi'
    }
)
if created:
    organizer1.set_password('password123')
    organizer1.save()
    organizer1.groups.add(organizer_group)
    UserProfile.objects.create(user=organizer1, role='organizer', bio='Professional event organizer', phone_number='+39 123 456 7890')

organizer2, created = User.objects.get_or_create(
    username='giulia_bianchi',
    defaults={
        'email': 'giulia.bianchi@event.com',
        'first_name': 'Giulia',
        'last_name': 'Bianchi'
    }
)
if created:
    organizer2.set_password('password123')
    organizer2.save()
    organizer2.groups.add(organizer_group)
    UserProfile.objects.create(user=organizer2, role='organizer', bio='Event organizer with 5 years experience', phone_number='+39 987 654 3210')

# Create attendee users
attendee1, created = User.objects.get_or_create(
    username='luca_verdi',
    defaults={
        'email': 'luca.verdi@email.com',
        'first_name': 'Luca',
        'last_name': 'Verdi'
    }
)
if created:
    attendee1.set_password('password123')
    attendee1.save()
    attendee1.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee1, role='attendee', bio='Technology enthusiast', phone_number='+39 111 222 3333')

attendee2, created = User.objects.get_or_create(
    username='anna_marini',
    defaults={
        'email': 'anna.marini@email.com',
        'first_name': 'Anna',
        'last_name': 'Marini'
    }
)
if created:
    attendee2.set_password('password123')
    attendee2.save()
    attendee2.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee2, role='attendee', bio='Loves networking events', phone_number='+39 444 555 6666')

attendee3, created = User.objects.get_or_create(
    username='carlo_rosini',
    defaults={
        'email': 'carlo.rosini@email.com',
        'first_name': 'Carlo',
        'last_name': 'Rosini'
    }
)
if created:
    attendee3.set_password('password123')
    attendee3.save()
    attendee3.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee3, role='attendee', bio='Business professional', phone_number='+39 777 888 9999')

# Create sample events
now = datetime.now()

event1, created = Event.objects.get_or_create(
    title='Python Conference 2025',
    defaults={
        'description': 'Una conferenza completa sullo sviluppo Python, framework web e migliori pratiche.',
        'organizer': organizer1,
        'location': 'Università di Firenze, Aula Magna',
        'start_date': now + timedelta(days=30),
        'end_date': now + timedelta(days=30, hours=8),
        'max_attendees': 100,
        'status': 'published'
    }
)

event2, created = Event.objects.get_or_create(
    title='Web Development Masterclass',
    defaults={
        'description': 'Impara tecniche avanzate di sviluppo web con Django, React e strumenti moderni.',
        'organizer': organizer2,
        'location': 'Online - Zoom',
        'start_date': now + timedelta(days=14),
        'end_date': now + timedelta(days=14, hours=4),
        'max_attendees': 50,
        'status': 'published'
    }
)

event3, created = Event.objects.get_or_create(
    title='Artificial Intelligence Workshop',
    defaults={
        'description': 'Workshop pratico su apprendimento automatico e fondamenta dell\'intelligenza artificiale.',
        'organizer': organizer1,
        'location': 'Campus Scientifico, Sesto Fiorentino',
        'start_date': now + timedelta(days=60),
        'end_date': now + timedelta(days=60, hours=6),
        'max_attendees': 30,
        'status': 'published'
    }
)

event4, created = Event.objects.get_or_create(
    title='Cloud Computing & DevOps',
    defaults={
        'description': 'Esplora le tecnologie cloud, Docker, Kubernetes e pratiche DevOps.',
        'organizer': organizer2,
        'location': 'Innovation Hub, Via dei Servi',
        'start_date': now + timedelta(days=45),
        'end_date': now + timedelta(days=45, hours=5),
        'max_attendees': 75,
        'status': 'published'
    }
)

event5, created = Event.objects.get_or_create(
    title='Workshop di Networking Avanzato',
    defaults={
        'description': 'Un workshop esclusivo per professionisti che desiderano migliorare le loro competenze di networking e creare connessioni strategiche.',
        'organizer': organizer2,
        'location': 'Sala Conferenze Palazzo Vecchio, Firenze',
        'start_date': now + timedelta(days=10),
        'end_date': now + timedelta(days=10, hours=3),
        'max_attendees': 2,
        'status': 'published'
    }
)

event6, created = Event.objects.get_or_create(
    title='Cybersecurity & Data Protection Summit',
    defaults={
        'description': 'Un summit completo sulla sicurezza informatica, protezione dei dati personali (GDPR) e best practices per aziende moderne.',
        'organizer': organizer1,
        'location': 'Centro Congressi, Piazza della Libertà 10, Firenze',
        'start_date': now + timedelta(days=20),
        'end_date': now + timedelta(days=20, hours=6),
        'max_attendees': 60,
        'status': 'published',
        'deleted_at': now  # Soft delete: evento marcato come eliminato
    }
)

event7, created = Event.objects.get_or_create(
    title='PPM',
    defaults={
        'description': 'Corso di progettazione e produzione multimediale',
        'organizer': organizer1,
        'location': 'Centro didattico Morgani - UNIFI, Firenze',
        'start_date': now - timedelta(days=20, hours=6),
        'end_date': now - timedelta(days=20),
        'max_attendees': 60,
        'status': 'published',
        'deleted_at': now - timedelta(days=21)  # Soft delete: evento marcato come eliminato
    }
)

# Create registrations
events = [event1, event2, event3, event4, event5, event6, event7]
attendees = [attendee1, attendee2, attendee3]

for event in events:
    for i, attendee in enumerate(attendees):
        reg, created = EventRegistration.objects.get_or_create(
            event=event,
            user=attendee,
            defaults={'status': 'confirmed' if i < 2 else 'pending'}
        )

# Specific registrations for event5 (only 2 attendees: Luca Verdi and Anna Marini)
EventRegistration.objects.get_or_create(
    event=event5,
    user=attendee1,  # Luca Verdi
    defaults={'status': 'confirmed'}
)
EventRegistration.objects.get_or_create(
    event=event5,
    user=attendee2,  # Anna Marini
    defaults={'status': 'confirmed'}
)

# Create some attendance records (mark some registrations as attended)
registrations = EventRegistration.objects.filter(status='confirmed').order_by('-registered_at')[:3]
for reg in registrations:
    EventAttendance.objects.get_or_create(registration=reg)

print("Database populated successfully!")
print(f"- Created/Updated {User.objects.count()} users")
print(f"- Created/Updated {Event.objects.count()} events")
print(f"- Created/Updated {EventRegistration.objects.count()} registrations")
print(f"- Created/Updated {EventAttendance.objects.count()} attendance records")
print(f"- Groups configured: {Group.objects.count()} groups")
print(f"\n📌 Eventi eliminati (soft delete):")
deleted_events = Event.objects.filter(deleted_at__isnull=False)
for event in deleted_events:
    print(f"   - {event.title} (organizzato da {event.organizer.first_name} {event.organizer.last_name}, eliminato il {event.deleted_at.strftime('%Y-%m-%d %H:%M')})")