#!/usr/bin/env python
import os
import django
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.files import File

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
now = timezone.now()

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
        'max_attendees': 2,
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
        'max_attendees': 30,
        'status': 'published'
    }
)

event5, created = Event.objects.get_or_create(
    title='PPM',
    defaults={
        'description': 'Corso di progettazione e produzione multimediale',
        'organizer': organizer2,
        'location': 'Centro didattico Morgani - UNIFI, Firenze',
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
    title='Workshop di Networking Avanzato',
    defaults={
        'description': 'Un workshop esclusivo per professionisti che desiderano migliorare le loro competenze di networking e creare connessioni strategiche.',
        'organizer': organizer1,
        'location': 'Sala Conferenze Palazzo Vecchio, Firenze',
        'start_date': now - timedelta(days=20, hours=6),
        'end_date': now - timedelta(days=20),
        'max_attendees': 75,
        'status': 'published',
        'deleted_at': now - timedelta(days=21)  # Soft delete: evento marcato come eliminato
    }
)
#--------- inizio nuove voci--------------
# ==============================================
# NUOVI ORGANIZZATORI
# ==============================================

organizer3, created = User.objects.get_or_create(
    username='laura_neri',
    defaults={
        'email': 'laura.neri@event.com',
        'first_name': 'Laura',
        'last_name': 'Neri'
    }
)
if created:
    organizer3.set_password('password123')
    organizer3.save()
    organizer3.groups.add(organizer_group)
    UserProfile.objects.create(user=organizer3, role='organizer', bio='Organizzatrice di eventi culturali', phone_number='+39 123 456 7891')

organizer4, created = User.objects.get_or_create(
    username='andrea_ferrari',
    defaults={
        'email': 'andrea.ferrari@event.com',
        'first_name': 'Andrea',
        'last_name': 'Ferrari'
    }
)
if created:
    organizer4.set_password('password123')
    organizer4.save()
    organizer4.groups.add(organizer_group)
    UserProfile.objects.create(user=organizer4, role='organizer', bio='Specialista in eventi sportivi', phone_number='+39 123 456 7892')

organizer5, created = User.objects.get_or_create(
    username='elena_ricci',
    defaults={
        'email': 'elena.ricci@event.com',
        'first_name': 'Elena',
        'last_name': 'Ricci'
    }
)
if created:
    organizer5.set_password('password123')
    organizer5.save()
    organizer5.groups.add(organizer_group)
    UserProfile.objects.create(user=organizer5, role='organizer', bio='Esperta in conferenze tech', phone_number='+39 123 456 7893')

# ==============================================
# NUOVI PARTECIPANTI
# ==============================================

attendee4, created = User.objects.get_or_create(
    username='paolo_galli',
    defaults={
        'email': 'paolo.galli@email.com',
        'first_name': 'Paolo',
        'last_name': 'Galli'
    }
)
if created:
    attendee4.set_password('password123')
    attendee4.save()
    attendee4.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee4, role='attendee', bio='Appassionato di tecnologia', phone_number='+39 111 222 3334')

attendee5, created = User.objects.get_or_create(
    username='sofia_conti',
    defaults={
        'email': 'sofia.conti@email.com',
        'first_name': 'Sofia',
        'last_name': 'Conti'
    }
)
if created:
    attendee5.set_password('password123')
    attendee5.save()
    attendee5.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee5, role='attendee', bio='Studentessa universitaria', phone_number='+39 111 222 3335')

attendee6, created = User.objects.get_or_create(
    username='matteo_esposito',
    defaults={
        'email': 'matteo.esposito@email.com',
        'first_name': 'Matteo',
        'last_name': 'Esposito'
    }
)
if created:
    attendee6.set_password('password123')
    attendee6.save()
    attendee6.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee6, role='attendee', bio='Sviluppatore software', phone_number='+39 111 222 3336')

attendee7, created = User.objects.get_or_create(
    username='giulia_romano',
    defaults={
        'email': 'giulia.romano@email.com',
        'first_name': 'Giulia',
        'last_name': 'Romano'
    }
)
if created:
    attendee7.set_password('password123')
    attendee7.save()
    attendee7.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee7, role='attendee', bio='Marketing specialist', phone_number='+39 111 222 3337')

attendee8, created = User.objects.get_or_create(
    username='francesco_greco',
    defaults={
        'email': 'francesco.greco@email.com',
        'first_name': 'Francesco',
        'last_name': 'Greco'
    }
)
if created:
    attendee8.set_password('password123')
    attendee8.save()
    attendee8.groups.add(attendee_group)
    UserProfile.objects.create(user=attendee8, role='attendee', bio='Designer UX/UI', phone_number='+39 111 222 3338')

# ==============================================
# NUOVI EVENTI
# ==============================================

event8, created = Event.objects.get_or_create(
    title='Fiera del Libro',
    defaults={
        'description': 'La più grande fiera dell\'editoria con presentazioni, firmacopie e incontri con autori.',
        'organizer': organizer3,
        'location': 'Centro Fieristico, Padiglione A',
        'start_date': now + timedelta(days=25),
        'end_date': now + timedelta(days=27, hours=8),
        'max_attendees': 500,
        'status': 'published'
    }
)

event9, created = Event.objects.get_or_create(
    title='Torneo di Basket a Squadre',
    defaults={
        'description': 'Torneo amatoriale di basket aperto a tutte le squadre della città.',
        'organizer': organizer4,
        'location': 'Palazzetto dello Sport',
        'start_date': now + timedelta(days=35),
        'end_date': now + timedelta(days=35, hours=6),
        'max_attendees': 120,
        'status': 'published'
    }
)

event10, created = Event.objects.get_or_create(
    title='Workshop di Sviluppo Mobile',
    defaults={
        'description': 'Impara a creare app per iOS e Android con React Native e Flutter.',
        'organizer': organizer5,
        'location': 'Laboratorio Informatico, Piano Terra',
        'start_date': now + timedelta(days=18),
        'end_date': now + timedelta(days=18, hours=5),
        'max_attendees': 30,
        'status': 'published'
    }
)

event11, created = Event.objects.get_or_create(
    title='Concerto di Musica Classica',
    defaults={
        'description': 'Un concerto serale con le più belle sinfonie di Mozart, Beethoven e Chopin.',
        'organizer': organizer3,
        'location': 'Auditorium Comunale',
        'start_date': now + timedelta(days=50),
        'end_date': now + timedelta(days=50, hours=3),
        'max_attendees': 200,
        'status': 'published'
    }
)

event12, created = Event.objects.get_or_create(
    title='Maratona di Programmazione',
    defaults={
        'description': 'Competizione di programmazione a squadre con problemi di algoritmi e strutture dati.',
        'organizer': organizer5,
        'location': 'Centro Congressi, Sala Code',
        'start_date': now + timedelta(days=40),
        'end_date': now + timedelta(days=40, hours=10),
        'max_attendees': 80,
        'status': 'published'
    }
)

event13, created = Event.objects.get_or_create(
    title='Torneo di Scacchi Online',
    defaults={
        'description': 'Torneo di scacchi a eliminazione diretta. Aperto a tutti i livelli.',
        'organizer': organizer4,
        'location': 'Piattaforma Online - Discord',
        'start_date': now + timedelta(days=12),
        'end_date': now + timedelta(days=12, hours=5),
        'max_attendees': 64,
        'status': 'published'
    }
)

event14, created = Event.objects.get_or_create(
    title='Conferenza su Intelligenza Artificiale',
    defaults={
        'description': 'Conferenza con esperti del settore su AI, Machine Learning e Deep Learning.',
        'organizer': organizer5,
        'location': 'Centro Innovazione, Sala AI',
        'start_date': now + timedelta(days=55),
        'end_date': now + timedelta(days=55, hours=8),
        'max_attendees': 150,
        'status': 'published'
    }
)

event15, created = Event.objects.get_or_create(
    title='Corso di Fotografia Digitale',
    defaults={
        'description': 'Corso base di fotografia: esposizione, composizione, editing con Lightroom.',
        'organizer': organizer3,
        'location': 'Studio Fotografico, Via delle Arti',
        'start_date': now + timedelta(days=22),
        'end_date': now + timedelta(days=22, hours=4),
        'max_attendees': 20,
        'status': 'published'
    }
)

event16, created = Event.objects.get_or_create(
    title='Seminario di Marketing Digitale',
    defaults={
        'description': 'Strategie di marketing sui social media, SEO e pubblicità online.',
        'organizer': organizer1,
        'location': 'Centro Formazione, Sala Executive',
        'start_date': now + timedelta(days=28),
        'end_date': now + timedelta(days=28, hours=6),
        'max_attendees': 60,
        'status': 'published'
    }
)

# ==============================================
# EVENTI PASSATI
# ==============================================

event17, created = Event.objects.get_or_create(
    title='Hackathon per Startup',
    defaults={
        'description': 'Hackathon di 48 ore per sviluppare soluzioni innovative per startup.',
        'organizer': organizer5,
        'location': 'Innovation Hub',
        'start_date': now - timedelta(days=45),
        'end_date': now - timedelta(days=43),
        'max_attendees': 100,
        'status': 'published'
    }
)

event18, created = Event.objects.get_or_create(
    title='Cena di Gala Benefica',
    defaults={
        'description': 'Cena di raccolta fondi per enti di beneficenza locali.',
        'organizer': organizer3,
        'location': 'Grand Hotel, Sala Ricevimenti',
        'start_date': now - timedelta(days=10),
        'end_date': now - timedelta(days=10, hours=4),
        'max_attendees': 150,
        'status': 'published'
    }
)

event19, created = Event.objects.get_or_create(
    title='Torneo di Tennis',
    defaults={
        'description': 'Torneo amatoriale di tennis singolare e doppio.',
        'organizer': organizer4,
        'location': 'Circolo Tennis, Campi 1-4',
        'start_date': now - timedelta(days=30),
        'end_date': now - timedelta(days=28),
        'max_attendees': 32,
        'status': 'published'
    }
)

# ==============================================
# EVENTI PER OGGI (UTILI PER IL FILTRO date_filter=today)
# ==============================================

event20, created = Event.objects.get_or_create(
    title='Networking Day - Edizione Primaverile',
    defaults={
        'description': 'Giornata di networking tra professionisti del settore tecnologico.',
        'organizer': organizer1,
        'location': 'Centro Eventi, Sala Meeting',
        'start_date': now,
        'end_date': now + timedelta(hours=6),
        'max_attendees': 80,
        'status': 'published'
    }
)

event21, created = Event.objects.get_or_create(
    title='Workshop di Team Building',
    defaults={
        'description': 'Attività e giochi per migliorare la collaborazione in team.',
        'organizer': organizer2,
        'location': 'Parco Urbano, Area Picnic',
        'start_date': now,
        'end_date': now + timedelta(hours=4),
        'max_attendees': 40,
        'status': 'published'
    }
)

event22, created = Event.objects.get_or_create(
    title='Presentazione Nuovo Software',
    defaults={
        'description': 'Lancio e dimostrazione del nuovo software di gestione aziendale.',
        'organizer': organizer5,
        'location': 'Auditorium Tech, Sala Demo',
        'start_date': now,
        'end_date': now + timedelta(hours=3),
        'max_attendees': 120,
        'status': 'published'
    }
)

# ==============================================
# REGISTRAZIONI PER I NUOVI EVENTI
# ==============================================

all_attendees = [attendee1, attendee2, attendee3, attendee4, attendee5, attendee6, attendee7, attendee8]
new_events = [event8, event9, event10, event11, event12, event13, event14, event15, event16, event17, event18, event19, event20, event21, event22]

for event in new_events:
    print(f"\nRegistrazioni per evento: {event.title} (max {event.max_attendees} partecipanti)")
    for attendee in all_attendees[:4]:  # Primi 4 partecipanti
        confermati = EventRegistration.objects.filter(
            event=event,
            status='confirmed'
        ).count()

        if event.max_attendees is None or confermati < event.max_attendees:
            stato_finale = 'confirmed'
            evento = 'CONFERMATO'
        else:
            stato_finale = 'pending'
            evento = 'IN LISTA ATTESA'

        print(f"   {evento} -> {attendee.username}")

        EventRegistration.objects.get_or_create(
            event=event,
            user=attendee,
            defaults={'status': stato_finale}
        )

# ==============================================
# AGGIUNGI ALCUNI ORGANIZZATORI COME PARTECIPANTI
# ==============================================

EventRegistration.objects.get_or_create(event=event10, user=organizer3, defaults={'status': 'confirmed'})
EventRegistration.objects.get_or_create(event=event12, user=organizer4, defaults={'status': 'confirmed'})
EventRegistration.objects.get_or_create(event=event14, user=organizer1, defaults={'status': 'pending'})
EventRegistration.objects.get_or_create(event=event20, user=organizer2, defaults={'status': 'confirmed'})
#--------- fine nuove voci--------------

# Create registrations
events = [event1, event2, event3, event4, event5, event6, event7]
attendees = [attendee1, attendee2, attendee3]

for event in events:
    print(f"\nRegistrazioni per evento: {event.title} (max {event.max_attendees} partecipanti)")
    for attendee in attendees:
        # Conta quanti sono già confermati
        confermati = EventRegistration.objects.filter(
            event=event,
            status='confirmed'
        ).count()

        # Decidi lo stato in base ai posti disponibili
        if event.max_attendees is None or confermati < event.max_attendees:
            stato_finale = 'confirmed'
            if event.max_attendees:
                print(f"   ✅ {attendee.username} → CONFERMATO (posto {confermati + 1}/{event.max_attendees})")
            else:
                print(f"   ✅ {attendee.username} → CONFERMATO (posto {confermati + 1}/illimitato)")
        else:
            stato_finale = 'pending'
            print(f"   ⏳ {attendee.username} → IN LISTA D'ATTESA (evento pieno)")

        # Crea o aggiorna la registrazione
        reg, created = EventRegistration.objects.get_or_create(
            event=event,
            user=attendee,
            defaults={'status': stato_finale}
        )

reg, created = EventRegistration.objects.get_or_create(
            event=event5,
            user=organizer1,
            defaults={'status': 'pending'}
        )

if not event5.image:
        image_path = 'event_images/morgagni.jpg'
        event5.image = image_path
        event5.save()
        print(f"   ✅ Immagine associata a {event5.title}")

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
#---print nuove voci----
print("\n" + "="*50)
print("AGGIUNTE COMPLETATE!")
print("="*50)
print(f"Nuovi organizzatori: {organizer3.username}, {organizer4.username}, {organizer5.username}")
print(f"Nuovi partecipanti: {attendee4.username}, {attendee5.username}, {attendee6.username}, {attendee7.username}, {attendee8.username}")
print(f"Nuovi eventi creati: {len(new_events)}")
print("="*50)
#-----------------------
print(f"\n📌 Eventi eliminati (soft delete):")
deleted_events = Event.objects.filter(deleted_at__isnull=False)
for event in deleted_events:
    print(f"   - {event.title} (organizzato da {event.organizer.first_name} {event.organizer.last_name}, eliminato il {event.deleted_at.strftime('%Y-%m-%d %H:%M')})")