# Event Management System – Full-Stack Web Application

**Studente:** Riccardo [Inserisci il tuo cognome]
**Data di submit:** 27 Maggio 2026
**Tipo progetto:** Full-Stack Web Application
**Framework:** Django
**Database SQLite incluso (locale):** db.sqlite3 (pre-popolato con demo data)

## Descrizione

Applicazione web per la gestione di eventi. Gli utenti con ruolo Attendee possono visualizzare gli eventi, registrarsi e annullare la propria partecipazione. Gli utenti con ruolo Organizer possono creare, modificare e cancellare i propri eventi, oltre a visualizzare la lista dei partecipanti. Il sistema utilizza un modello Profile (UserProfile) esteso rispetto all'utente base di Django.

## Funzionalità per ruolo

### Attendee (utente standard)

- Visualizzare lista eventi e dettaglio singolo evento
- Registrarsi a un evento (crea una registrazione nel modello EventRegistration)
- Visualizzare le proprie registrazioni
- Annullare la propria registrazione
- Visualizzare il calendario degli eventi registrati

### Organizer (gestore eventi)

- Tutte le funzionalità di Attendee
- Creare nuovi eventi (tramite EventCreateView)
- Modificare e cancellare solo i propri eventi (tramite EventUpdateView e EventDeleteView)
- Visualizzare gli iscritti ai propri eventi e gestire le registrazioni
- Accedere alla pagina "I Miei Eventi" per gestire l'intera lista dei propri eventi

### Amministratore (superuser)

- Accesso al pannello admin di Django
- Gestire utenti, profili (UserProfile), eventi, registrazioni e presenze
- Visualizzare tutti gli eventi e utenti del sistema
- Accesso alla pagina degli "Eventi Eliminati" per ripristinare eventi soft-deleted

## Demo account inclusi

Ruolo | Username | Password
--- | --- | ---
Amministratore | admin | admin123
Organizer | marco_rossi | password123
Attendee | luca_verdi | password123

## Modelli (relazioni)

- User (Django built-in, esteso con UserProfile)
- UserProfile (OneToOne con User, contiene ruolo, bio, numero telefono, foto profilo)
- Event (ForeignKey verso User come organizzatore)
- EventRegistration (relazione Many-to-Many tra User ed Event per le registrazioni, con status: pending/confirmed/cancelled/attended)
- EventAttendance (OneToOne con EventRegistration, tracciamento presenza)

### Relazioni implementate

- Event.organizer → ForeignKey a User
- EventRegistration.event → ForeignKey a Event
- EventRegistration.user → ForeignKey a User
- EventAttendance.registration → OneToOne a EventRegistration
- UserProfile.user → OneToOne a User

## Installazione locale

### Prerequisiti

- Python 3.8 o superiore
- pip
- git

### Passaggi

1. Clona il repository
   git clone <repo-url>
   cd EventMenagementSystem

2. Crea e attiva un ambiente virtuale
   python -m venv venv
   source venv/bin/activate  (Windows: venv\Scripts\activate)

3. Installa le dipendenze
   pip install -r requirements.txt

4. (Opzionale) Applica le migrazioni
   python manage.py migrate
   
   Nota: Il database incluso (db.sqlite3) è già aggiornato. Esegui questo comando solo se aggiungi nuove migrazioni.

5. Avvia il server locale
   python manage.py runserver
   
   Accedi a http://localhost:8000/

Nota importante: Il file db.sqlite3 è già incluso e contiene tutti i dati demo (eventi, registrazioni, account). Non è necessario caricare fixture.

## Deployment online

L'applicazione è accessibile su Railway all'indirizzo:
https://eventmenagementsystem.up.railway.app

### Nota sul database di produzione

Il server di produzione utilizza un database PostgreSQL indipendente. Per testare il progetto deployato con i demo account, utilizzare le medesime credenziali del database locale.

## Testing da browser (scenario consigliato)

### Test 1: Creazione e gestione evento (Organizer)

1. Login come Organizer
   - Username: marco_rossi
   - Password: password123

2. Crea un nuovo evento
   - Clicca su "Create Event" (nella barra di navigazione)
   - Compila il modulo:
     - Titolo: "Workshop Django Avanzato"
     - Descrizione: "Un workshop pratico su Django"
     - Luogo: "Aula 101"
     - Data/ora inizio: [data]
     - Data/ora fine: [dopo l'inizio]
     - Numero massimo partecipanti: 20
     - Stato: "published"
   - Clicca "Create"

3. Verifica l'evento creato
   - Vai a "I Miei Eventi" → vedi l'evento appena creato
   - Clicca su dettaglio evento
   - Usa il pulsante "Update" per modificare il titolo

4. Gestisci l'evento
   - Visualizza la lista degli iscritti
   - Prova a promuovere utenti dalla lista d'attesa

### Test 2: Registrazione e gestione iscrizioni (Attendee)

1. Logout da marco_rossi

2. Login come Attendee
   - Username: luca_verdi
   - Password: password123

3. Registrati a un evento
   - Vai a "Lista Eventi"
   - Seleziona l'evento creato dall'Organizer
   - Clicca "Iscriviti"
   - Verifica il messaggio di successo

4. Visualizza le tue iscrizioni
   - Vai a "Le mie registrazioni"
   - Vedi l'evento con stato "Confermato"
   - Clicca "Disiscriviti" e conferma la disiscrizione

### Test 3: Controllo dei permessi

1. Prova accesso non autorizzato come Attendee
   - Tenta di accedere direttamente a /events/create/
   - Sistema nega accesso con messaggio di errore

2. Prova modifica evento di altri Organizer
   - Login come Organizer
   - Prova a modificare un evento creato da un altro organizer (se presente)
   - Sistema nega accesso

3. Verifica permessi nel frontend
   - Come Attendee, visualizza evento di un organizer
   - Pulsante "Update" e "Delete" non visibili
   - Come Organizer, visualizza tuo evento
   - Pulsanti "Update" e "Delete" visibili

### Test 4: Sistema di waiting list

1. Crea evento con 1 posto disponibile
   - Login come marco_rossi
   - Create Event con max_attendees = 1

2. Iscrivi primo utente
   - Login come luca_verdi
   - Registrati all'evento → stato "Confermato"

3. Iscrivi secondo utente
   - Crea nuovo account (es. giorgia_rossi / password123)
   - Registrati allo stesso evento → stato "In Attesa"

4. Testa promozione automatica
   - Login come luca_verdi
   - Vai a "My Registrations"
   - Clicca "Unregister"
   - Verifica che giorgia_rossi riceva notifica di promozione

## Struttura del progetto
```
EventMenagementSystem/
├── eventmenagementsystem/ (Configurazione principale Django)
│   ├── settings.py (Configurazione progetto)
│   ├── urls.py (URL routing principale)
│   ├── wsgi.py (WSGI per deployment)
│   └── asgi.py (ASGI per async)
├── events/ (App principale per gestione eventi)
│   ├── models.py (Event, EventRegistration, EventAttendance)
│   ├── views.py (Class-based views: ListView, DetailView, CreateView, UpdateView, DeleteView)
│   ├── forms.py (EventForm con validazioni)
│   ├── urls.py (URL routing per events)
│   ├── admin.py (Admin panel configuration)
│   ├── migrations/ (Migrazioni database)
│   └── templates/events/ (Template HTML per eventi)
├── users/ (App per gestione utenti e autenticazione)
│   ├── models.py (UserProfile)
│   ├── views.py (Autenticazione, profilo, list/detail)
│   ├── urls.py (URL routing per users)
│   ├── admin.py (Admin configuration)
│   └── templates/users/ (Template HTML per login/register/profile)
├── templates/ (Template globali: base.html, home.html)
├── static/ (File statici: CSS, JS, favicon)
├── media/ (Media caricati: event_images/, profile_pictures/)
├── db.sqlite3 (Database SQLite pre-popolato)
├── manage.py (Django management script)
├── requirements.txt (Dipendenze Python)
└── README.md (Questo file)
```
## Tecnologie utilizzate

- Backend: Django 6.0.4
- Database: SQLite (locale) / PostgreSQL (production)
- Frontend: HTML5, CSS3, Bootstrap
- Server WSGI: Gunicorn (production)
- Gestione statico: WhiteNoise (production)
- Validazione immagini: Pillow 12.2.0
- Environment variables: python-decouple

## Funzionalità avanzate implementate

### Class-based views

Tutte le operazioni CRUD sugli eventi sono gestite da classi generiche di Django:

- EventListView → ListView con filtri avanzati (ricerca testuale, data, organizzatore)
- EventDetailView → DetailView con visualizzazione iscritti e pending list
- EventCreateView → CreateView con permessi (solo organizers autenticati)
- EventUpdateView → UpdateView con permessi (solo organizzatore dell'evento o admin)
- EventDeleteView → DeleteView con soft-delete (ripristinabile entro 3 giorni)

### Sistema di waiting list

Se un evento raggiunge il massimo di partecipanti:
- Le nuove registrazioni entrano in stato "pending" (lista d'attesa)
- Quando un partecipante si ritira, il primo in lista viene promosso automaticamente a "confirmed"
- Notifiche tramite Django messages

### Soft delete di eventi

Gli eventi eliminati non vengono cancellati dal database:
- Segnati con timestamp deleted_at
- Possono essere ripristinati entro 3 giorni
- Dopo 3 giorni, gli admin possono eliminarli definitivamente
- Gli utenti non vedono gli eventi soft-deleted (solo admin e organizzatore possono vederli)

### Validazioni implementate

- Validazione date evento (inizio < fine)
- Validazione numero partecipanti (> 0 o illimitato)
- Validazione dimensione immagine (max 2MB)
- Controllo permessi su tutte le operazioni sensibili (create/update/delete)
- Prevenzione auto-registrazione ai propri eventi
- Validazione unica EventRegistration (event, user)

### Ricerca e filtri avanzati

- Ricerca testuale per titolo, descrizione, luogo, organizzatore
- Filtri per data (oggi, prossimi, passati, range personalizzato)
- Filtri per organizzatore
- Filtri per stato registrazione (confermato, in attesa, annullato)

## API endpoints e viste

| Metodo | URL | Autenticazione | Ruolo Richiesto | Descrizione |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | No | Tutti | Home page principale |
| **GET** | `/admin/` | Sì | Admin | Admin panel di Django |
| **GET** | `/events/` | No | Tutti | Lista eventi pubblicati con filtri avanzati |
| **GET** | `/events/event/<id>/` | No | Tutti | Dettaglio evento e lista iscritti |
| **POST** | `/events/create/` | Sì | Organizer | Crea nuovo evento |
| **POST** | `/events/event/<id>/edit/` | Sì | Organizer | Modifica evento (solo proprietario) |
| **POST** | `/events/event/<id>/delete/` | Sì | Organizer | Soft-delete evento (solo proprietario) |
| **POST** | `/events/event/<id>/register/` | Sì | Attendee | Registrati a evento |
| **POST** | `/events/event/<id>/unregister/` | Sì | Attendee | Cancella registrazione |
| **GET** | `/events/event/<id>/unregister/confirm/` | Sì | Attendee | Pagina conferma disiscrizione |
| **POST** | `/events/event/<id>/unregister/confirm/` | Sì | Attendee | Conferma disiscrizione e promozione waiting list |
| **GET** | `/events/my-registrations/` | Sì | Attendee | Visualizza proprie iscrizioni con filtri |
| **GET** | `/events/my-events/` | Sì | Organizer | Visualizza propri eventi con filtri |
| **GET** | `/events/deleted-events/` | Sì | Admin | Visualizza eventi eliminati con timer ripristino (3 giorni) |
| **POST** | `/events/event/<id>/restore/` | Sì | Admin/Organizer | Ripristina evento eliminato se entro 3 giorni |
| **GET** | `/events/event/<event_id>/admin-unregister/<registration_id>/confirm/` | Sì | Admin/Organizer | Pagina conferma disiscrivere utente |
| **POST** | `/events/event/<event_id>/unregister-user/<registration_id>/` | Sì | Admin/Organizer | Disiscrive utente e promuove da waiting list |
| **GET** | `/events/event/<id>/admin-register/<registration_pk>/confirm/` | Sì | Admin/Organizer | Pagina conferma promozione waiting list |
| **POST** | `/events/event/<id>/register-user/<registration_pk>/` | Sì | Admin/Organizer | Promuove utente da pending a confirmed |
| **GET** | `/events/calendar/` | Sì | Attendee | Calendario interattivo degli eventi registrati (FullCalendar) |
| **GET** | `/events/api/calendar-events/` | Sì | Attendee | API JSON per calendario con eventi (registrati e organizzati) |
| **POST** | `/users/register/` | No | Tutti | Registra nuovo utente |
| **POST** | `/users/login/` | No | Tutti | Login utente |
| **POST** | `/users/logout/` | Sì | Tutti | Logout utente |
| **GET** | `/users/profile/` | Sì | Tutti | Visualizza e modifica profilo personale |
| **POST** | `/users/profile/` | Sì | Tutti | Salva modifiche profilo (bio, telefono, nome, email) |
| **GET** | `/users/admin/users/` | Sì | Admin | Lista di tutti gli utenti con filtri e statistiche |
| **GET** | `/users/admin/users/<user_id>/` | Sì | Admin | Dettaglio singolo utente (eventi creati, iscrizioni) |
| **GET** | `/users/admin/organizers/` | Sì | Admin | Lista organizzatori con statistiche (n. eventi, partecipanti totali, ordinamento) |

---

Ultimo aggiornamento: 27 Maggio 2026

---