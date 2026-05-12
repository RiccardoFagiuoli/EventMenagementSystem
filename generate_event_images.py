#!/usr/bin/env python
import os
import django
import shutil
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files import File
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventmenagementsystem.settings')
django.setup()

from events.models import Event

def clean_media_event_images(keep_files=None):
    """
    Pulisce la cartella media/event_images mantenendo solo i file specificati
    e le immagini attualmente associate agli eventi nel database.

    Args:
        keep_files: Lista di nomi di file da mantenere (es. ['morgagni.jpg'])
    """
    if keep_files is None:
        keep_files = ['morgagni.jpg']

    # Percorso della cartella event_images
    event_images_path = 'media/event_images'

    # Verifica che la cartella esista
    if not os.path.exists(event_images_path):
        print(f"📁 Cartella {event_images_path} non trovata. Nessuna pulizia necessaria.")
        return

    # Raccogli i file da mantenere (quelli specificati manualmente)
    files_to_keep = set(keep_files)

    # Aggiungi le immagini attualmente associate agli eventi nel database
    events_with_images = Event.objects.exclude(image='')
    print("\n📌 Immagini attualmente associate a eventi nel database:")
    for event in events_with_images:
        if event.image:
            # Estrai il nome del file dal percorso
            image_filename = os.path.basename(event.image.name)
            files_to_keep.add(image_filename)
            print(f"   🔒 {image_filename} → {event.title[:40]}")

    # Mostra i file che verranno mantenuti
    print(f"\n📋 File da mantenere:")
    for f in files_to_keep:
        print(f"   ✅ {f}")

    # Pulisci la cartella event_images
    print(f"\n🧹 Pulizia cartella {event_images_path}...")
    deleted_count = 0
    kept_count = 0

    for filename in os.listdir(event_images_path):
        file_path = os.path.join(event_images_path, filename)

        # Salta se è un file da mantenere
        if filename in files_to_keep:
            kept_count += 1
            print(f"   📁 Mantenuto: {filename}")
            continue

        # Elimina il file
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"   🗑️ Eliminato: {filename}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                deleted_count += 1
                print(f"   🗑️ Eliminata cartella: {filename}/")
        except Exception as e:
            print(f"   ❌ Errore eliminando {filename}: {e}")

    # Statistiche finali
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO PULIZIA")
    print("=" * 50)
    print(f"   File mantenuti: {kept_count}")
    print(f"   File eliminati: {deleted_count}")

    # Conta cosa rimane
    remaining = os.listdir(event_images_path)
    print(f"\n📁 File rimasti in media/event_images/ ({len(remaining)}):")
    for f in remaining:
        print(f"   📄 {f}")


def clean_only_unused_images(keep_files=None):
    """
    Elimina SOLO le immagini non associate a nessun evento nel database
    (mantiene quelle collegate anche se non in keep_files)
    """
    if keep_files is None:
        keep_files = ['morgagni.jpg']

    event_images_path = 'media/event_images'

    if not os.path.exists(event_images_path):
        print(f"📁 Cartella {event_images_path} non trovata.")
        return

    # Raccogli TUTTE le immagini usate dagli eventi
    used_images = set()
    events_with_images = Event.objects.exclude(image='')
    for event in events_with_images:
        if event.image:
            used_images.add(os.path.basename(event.image.name))

    # Aggiungi i file protetti manualmente
    for f in keep_files:
        used_images.add(f)

    print(f"\n📋 Immagini in uso/da proteggere ({len(used_images)}):")
    for img in used_images:
        print(f"   🔒 {img}")

    # Pulisci
    print(f"\n🧹 Pulizia cartella {event_images_path}...")
    deleted_count = 0

    for filename in os.listdir(event_images_path):
        file_path = os.path.join(event_images_path, filename)

        if filename in used_images:
            print(f"   📁 Mantenuto: {filename}")
            continue

        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"   🗑️ Eliminato: {filename}")
        except Exception as e:
            print(f"   ❌ Errore: {e}")

    print(f"\n✅ Eliminati {deleted_count} file non utilizzati.")


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("🧹 PULIZIA CARTELLA media/event_images/")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "--unused-only":
        # Elimina solo file non usati (più sicuro)
        clean_only_unused_images(keep_files=['morgagni.jpg'])
    else:
        # Pulizia completa (mantiene file specificati + quelli usati)
        clean_media_event_images(keep_files=['morgagni.jpg'])

    print("\n✅ Operazione completata!")

def generate_event_image(event_title, event_date, output_path):
    """
    Genera un'immagine placeholder per un evento
    """
    # Dimensioni immagine
    width, height = 800, 600

    # Crea un'immagine con sfondo gradiente
    img = Image.new('RGB', (width, height), color=(102, 126, 234))

    # Disegna un gradiente semplice
    draw = ImageDraw.Draw(img)

    start_color = (102, 126, 234)  # #667eea
    end_color = (118, 75, 162)  #4b6cb7

    # Aggiungi un rettangolo decorativo in basso
    for x in range(width):
        # Calcola il fattore di mix basato sulla posizione Y (per angolo 135deg)
        # Simula un gradiente diagonale
        ratio = x / width
        # Mescola i colori
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

        # Disegna una riga orizzontale con il colore calcolato
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    # Colori per i testi
    title_color = (255, 255, 255)
    date_color = (255, 255, 255)

    # Font sizes - prova diversi font di sistema
    try:
        # Prova font Windows
        title_font = ImageFont.truetype("arial.ttf", 45)
        date_font = ImageFont.truetype("arial.ttf", 30)
    except:
        try:
            # Prova font alternativo Windows
            title_font = ImageFont.truetype("segoeui.ttf", 45)
            date_font = ImageFont.truetype("segoeui.ttf", 30)
        except:
            try:
                # Prova font Linux/Mac
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 45)
                date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
            except:
                # Fallback al font predefinito di Pillow
                title_font = ImageFont.load_default()
                date_font = ImageFont.load_default()

    # Accorcia il titolo se troppo lungo (max 40 caratteri)
    short_title = event_title[:40] + "..." if len(event_title) > 40 else event_title

    # Calcola posizione testo (centrato) usando textbbox
    try:
        # Per Pillow >= 8.0.0
        bbox = draw.textbbox((0, 0), short_title, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_height = bbox[3] - bbox[1]
    except AttributeError:
        # Per versioni più vecchie di Pillow
        title_width, title_height = draw.textsize(short_title, font=title_font)

    title_x = (width - title_width) // 2
    title_y = (height - 100) // 2

    # Disegna il titolo
    draw.text((title_x, title_y), short_title, fill=title_color, font=title_font)

    # Formatta la data
    date_text = " Immagine generata con script"

    # Calcola posizione data
    try:
        date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        date_height = date_bbox[3] - date_bbox[1]
    except AttributeError:
        date_width, date_height = draw.textsize(date_text, font=date_font)

    date_x = (width - date_width) // 2
    date_y = title_y + title_height + 20

    draw.text((date_x, date_y), date_text, fill=date_color, font=date_font)

    # Aggiungi un'icona decorativa (un cerchio nell'angolo)
    draw.ellipse([(width - 60, 20), (width - 20, 60)], fill=(46, 204, 113), outline=(255, 255, 255), width=2)

    # Aggiungi un altro cerchio nell'angolo opposto
    draw.ellipse([(20, height - 80), (60, height - 40)], fill=(231, 76, 60), outline=(255, 255, 255), width=2)

    # Salva l'immagine
    img.save(output_path, 'JPEG', quality=85)
    return output_path


def get_placeholder_image_path(event_title, event_date):
    """
    Crea un'immagine placeholder temporanea
    """
    # Crea directory se non esiste
    os.makedirs('media/event_images', exist_ok=True)

    # Nome file sicuro (solo caratteri alfanumerici)
    safe_title = ''.join(c for c in event_title[:30] if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
    filename = f"event_images/generated_{safe_title}.jpg"
    full_path = os.path.join('media', filename)

    # Genera l'immagine
    generate_event_image(event_title, event_date, full_path)

    return filename


def assign_images_to_events(percentage=50):
    """
    Assegna immagini generate al 50% degli eventi (scelta casuale)
    """
    # Prendi tutti gli eventi (escludi quelli già con immagine)
    all_events = list(Event.objects.filter(image=''))

    if not all_events:
        print("✅ Tutti gli eventi hanno già un'immagine!")
        return

    # Calcola quanti eventi devono ricevere un'immagine (50%)
    num_to_update = int(len(all_events) * percentage / 100)

    # Scegli casualmente quali eventi
    events_to_update = random.sample(all_events, num_to_update)

    print(f"\n📸 Generazione immagini per eventi...")
    print(f"   Totale eventi senza immagine: {len(all_events)}")
    print(f"   Eventi da aggiornare ({percentage}%): {num_to_update}")

    updated_count = 0
    for event in events_to_update:
        try:
            # Genera l'immagine
            image_path = get_placeholder_image_path(event.title, event.start_date)

            # Apri l'immagine e crea il Django File
            full_image_path = os.path.join('media', image_path)
            if os.path.exists(full_image_path):
                with open(full_image_path, 'rb') as f:
                    event.image.save(os.path.basename(image_path), File(f), save=True)
                updated_count += 1
                print(f"   ✅ {event.title[:40]}... → immagine aggiunta")
            else:
                print(f"   ❌ File non trovato per {event.title[:40]}...")

        except Exception as e:
            print(f"   ❌ Errore per {event.title[:40]}...: {str(e)}")

    print(f"\n✨ Completato! {updated_count} immagini generate e associate.")

    # Mostra statistiche finali
    events_with_image = Event.objects.exclude(image='').count()
    events_without_image = Event.objects.filter(image='').count()
    print(f"\n📊 Statistiche finali:")
    print(f"   Eventi con immagine: {events_with_image}")
    print(f"   Eventi senza immagine: {events_without_image}")


if __name__ == "__main__":
    # Imposta seed per riproducibilità (opzionale - commenta per casualità totale)
    # random.seed(42)

    # Assegna immagini al 50% degli eventi senza immagine
    assign_images_to_events(percentage=50)