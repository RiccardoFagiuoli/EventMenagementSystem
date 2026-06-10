# Event Management System

**Studente**: Riccardo Fagiuoli  
**Tipo di Progetto**: Full-Stack Web Application  
**Framework**: Django 6.0.4  

---

## 📌 Descrizione del Progetto

Event Management System è un'applicazione web completa che consente agli utenti di scoprire, registrarsi e partecipare a eventi. Gli organizzatori possono creare e gestire i loro eventi, visualizzare elenchi di partecipanti e gestire la coda d'attesa quando un evento è al completo.

L'applicazione è progettata con un'architettura modulare Django e include autenticazione, autorizzazione basata su ruoli, gestione delle immagini, soft delete degli eventi, e un sistema di waiting list automatico.

---

## 🎯 Funzionalità Implementate

### Per Partecipanti (Attendee)
-  Visualizzare tutti gli eventi pubblicati con dettagli completi
-  Ricerca e filtro degli eventi per titolo, descrizione, location
-  Registrazione e cancellazione dagli eventi
-  Sistema di waiting list automatico quando un evento è pieno
-  Visualizzazione delle proprie registrazioni (confermate, in attesa, cancellate)
-  Calendario interattivo delle proprie registrazioni confermate
-  Gestione profilo personale
-  Visualizzazione della propria storia registrazioni

### Per Organizzatori (Organizer)
-  Tutte le funzionalità dei Partecipanti
-  Creazione di nuovi eventi con immagini, data/ora inizio/fine, limite partecipanti
-  Modifica dei propri eventi
-  Soft delete degli eventi (ripristinabili entro 3 giorni)
-  Visualizzazione lista completa iscritti (confermati e in attesa)
-  Gestione manuale della waiting list (promozione da lista d'attesa)
-  Calendario degli eventi creati
-  Pagina dedicata "I miei eventi"

### Per Amministratori (Admin)
-  Accesso pannello Django Admin completo
-  Visualizzazione di TUTTI gli eventi (inclusi eliminati)
-  Gestione utenti e ruoli
-  Lista organizzatori con statistiche
-  Pagina degli eventi eliminati con timeline di ripristino
-  Tutte le funzionalità di organizer

---

## 🛠️ Installazione e Setup Locale

### Prerequisiti
- Python 3.10 o superiore
- pip (gestore pacchetti Python)
- Git

### Procedura di Installazione

1. **Clona il repository**
   ```bash
   git clone <repository-url>
   cd EventMenagementSystem
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python -m venv venv
   ```

3. **Attiva l'ambiente virtuale**
   - **Su Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Su Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Su macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

5. **Applica le migrazioni** (il database è già pre-popolato, ma esegui comunque)
   ```bash
   python manage.py migrate
   ```

6. **Avvia il server locale**
   ```bash
   python manage.py runserver
   ```

7. **Accedi all'applicazione**
   - URL: `http://127.0.0.1:8000/`
   - Django Admin: `http://127.0.0.1:8000/admin/`

---

## 📊 Database Pre-Popolato

Il progetto include il file **`db.sqlite3`** pre-popolato con:
-  2 organizzatori con eventi creati
-  5 partecipanti con varie iscrizioni
-  15+ eventi di esempio in vari stati (draft, published, completed, cancelled)
-  Registrazioni agli eventi con mix di status (confirmed, pending, cancelled, attended)
-  Account admin per accesso Django Admin

---

## 🔐 Account Demo Disponibili

| Username | Password | Ruolo | Descrizione |
|---------|----------|--------|-------------|
| `admin` | `admin123` | **Admin/Superuser** | Accesso completo, visione globale, Django Admin |
| `marco_rossi` | `password123` | **Organizer** | Può creare/modificare/eliminare eventi, gestisce iscritti |
| `luca_verdi` | `password123` | **Attendee** | Visualizza eventi, si registra, gestisce iscrizioni |

**Note**: Questi account sono creati esclusivamente per il testing della valutazione. Non sono account reali o personali.

---

## 🌐 Deployment Online

**URL di Produzione**: https://eventmenagementsystem.up.railway.app/

L'applicazione è deployata su **Railway** (piattaforma free con piano gratuito).

**Per accedere online, usa gli stessi account demo elencati sopra.**

---

## 📋 Scenario di Testaggio Completo (Browser)

### Test 1: Login e Navigazione Base (Attendee)
1. Vai a https://eventmenagementsystem.up.railway.app/
2. Accedi con: `luca_verdi` / `password123`
3. Visualizza la home page con statistiche eventi
4. Clicca su "Events" → vedi lista eventi pubblicati
5. Cerca un evento per titolo o location
6. Clicca su un evento → visualizza dettagli, organizzatore, numero iscritti

### Test 2: Registrazione e Gestione Iscrizioni (Attendee)
1. Rimani loggato come `luca_verdi`
2. Seleziona un evento non-pieno → clicca "Register"
3. Ricevi messaggio di conferma "Registrazione completata!"
4. Vai a "My Registrations" → vedi l'evento nella lista "Confirmed"
5. Seleziona un evento pieno (max_attendees raggiunto) → clicca "Register"
6. Ricevi messaggio "Evento al completo. Sei stato aggiunto alla lista d'attesa."
7. In "My Registrations" vedi lo status "Pending" per quell'evento
8. Torna su quell'evento → clicca "Unregister"
9. Ricevi conferma e vedi status cambiato a "Cancelled"

### Test 3: Cambio Ruolo a Organizer
1. Vai a "Profile" (menu utente)
2. Logout come `luca_verdi`
3. Accedi con: `marco_rossi` / `password123` (Organizer)
4. Vedi menu aggiuntivi: "Create Event" e "My Events"

### Test 4: Creazione Evento (Organizer)
1. Loggato come `marco_rossi`
2. Clicca "Create Event"
3. Compila il form:
   - Titolo: "Workshop Django"
   - Descrizione: "Impara Django in 4 ore"
   - Location: "Sala Conferenze B"
   - Data Inizio: oggi + 7 giorni, ore 14:00
   - Data Fine: stessa data, ore 18:00
   - Max Attendees: 5
   - Status: "Published"
   - Immagine: (facoltativa)
4. Clicca "Save"
5. Vieni reindirizzato a "My Events" e vedi il nuovo evento

### Test 5: Modifica e Soft Delete (Organizer)
1. Loggato come `marco_rossi`, in "My Events"
2. Seleziona il workshop creato → clicca "Edit"
3. Modifica descrizione → clicca "Save"
4. Torna a dettagli evento → clicca "Delete"
5. Ricevi messaggio "Evento eliminato con successo! Puoi ripristinarlo entro 3 giorni."
6. Clicca "Restore" → l'evento è attivo di nuovo

### Test 6: Permessi Assenti (Attendee non può creare)
1. Logout come `marco_rossi`
2. Accedi come `luca_verdi` (Attendee)
3. Prova a visitare: http://127.0.0.1:8000/events/create/
4. Ricevi messaggio di errore "Solo gli organizzatori possono creare eventi."
5. Sei reindirizzato a Event List

### Test 7: Admin Panel
1. Logout come `luca_verdi`
2. Accedi come `admin_demo` / `admin12345`
3. Vai su http://127.0.0.1:8000/admin/
4. Puoi visualizzare e modificare:
   - Event (tutti gli eventi inclusi eliminati)
   - EventRegistration
   - User e UserProfile
   - Puoi creare/editare/eliminare qualsiasi record

### Test 8: Validazione Form
1. Loggato come `marco_rossi`, vai a "Create Event"
2. Tenta di creare evento con **data fine PRIMA della data inizio**
3. Ricevi errore: "La data e ora di inizio deve essere precedente alla data e ora di fine."
4. Tenta di caricare immagine > 2MB
5. Ricevi errore: "L'immagine è troppo pesante (max 2MB)."

---

## 🗂️ Struttura del Progetto

```
EventMenagementSystem/
├── db.sqlite3                          # Database pre-popolato
├── manage.py                           # Django management
├── requirements.txt                    # Dipendenze Python
├── README.md                           # Questo file
├── Procfile                            # Configuration Railway
├── eventmenagementsystem/              # Configurazione Django principale
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── events/                             # App 1: Gestione Eventi
│   ├── models.py                       # Event, EventRegistration, EventAttendance
│   ├── views.py                        # 5 class-based views + function-based
│   ├── forms.py                        # EventForm con validazioni
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/                     # Migrazioni Django
│   └── templatetags/
│       └── custom_filters.py           # Custom template filters
├── users/                              # App 2: Gestione Utenti
│   ├── models.py                       # User, UserProfile
│   ├── views.py                        # Login, Register, Profile, Admin views
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── templates/                          # Template HTML
│   ├── base.html                       # Template base con navbar
│   ├── home.html
│   ├── events/                         # Template app events
│   │   ├── event_list.html
│   │   ├── event_detail.html
│   │   ├── event_form.html
│   │   ├── calendar.html
│   │   └── ...
│   └── users/                          # Template app users
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       └── ...
├── static/                             # File statici (CSS, JS, immagini)
│   └── favicon.ico
└── media/                              # File caricati (immagini eventi, profili)
    └── event_images/
```

---

## 🔧 Requisiti Tecnici Implementati

### Modelli e Relazioni
-  **Event**: Modello principale con ForeignKey a User (organizer)
-  **EventRegistration**: Relazione Many-to-Many tra User e Event
-  **EventAttendance**: OneToOneField a EventRegistration (presenza fisica)
-  **UserProfile**: OneToOneField a User (custom user profile)

### Autenticazione e Autorizzazione
-  Sistema login/logout con Django auth
-  Registrazione utenti con scelta del ruolo
-  2+ ruoli: Attendee, Organizer, Admin
-  Permessi enforced con LoginRequiredMixin, UserPassesTestMixin
-  Messaggi di errore quando l'accesso è negato

### Class-Based Views
-  EventListView (ListView)
-  EventDetailView (DetailView)
-  EventCreateView (CreateView)
-  EventUpdateView (UpdateView)
-  EventDeleteView (DeleteView)

### Validazione Input
-  EventForm con Django ModelForm
-  Validazioni custom: date coerenti, file size, numero partecipanti
-  Errori mostrati agli utenti tramite messages framework
-  Error messages user-friendly in italiano

### CRUD Completo
-  **Create**: EventCreateView, form valido
-  **Read**: EventListView, EventDetailView
-  **Update**: EventUpdateView
-  **Delete**: EventDeleteView (soft delete)
-  Permessi rispettati per organizer

---

## 🚀 Deployment su Railway

L'applicazione è deployata su Railway (https://railway.app/), una piattaforma cloud gratuita.

**URL Live**: https://eventmenagementsystem.up.railway.app/

### Caratteristiche del Deployment
-  Django in modalità produzione
-  Database SQLite persistente
-  Media files serviti correttamente
-  Static files compressati con WhiteNoise
-  Login e tutte le funzionalità funzionanti online

---

## 📝 Note Tecniche

- **Soft Delete**: Gli eventi eliminati rimangono nel database per 3 giorni e possono essere ripristinati
- **Waiting List Automatica**: Quando un evento raggiunge il limite, nuovi iscritti vengono automaticamente aggiunti alla lista d'attesa
- **Promotion Automatica**: Quando qualcuno si cancella, il primo della waiting list viene promosso automaticamente
- **Timezone**: Europe/Rome (UTC+1 o UTC+2 a seconda dell'ora legale)
- **Paginazione**: Event list pagina 10 eventi per pagina, Admin views 20 utenti per pagina


**Ultimo aggiornamento**: Giugno 2026  
**Versione**: 1.0
