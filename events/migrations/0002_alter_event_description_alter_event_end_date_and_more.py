import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(verbose_name='Descrizione'),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(verbose_name='Data e Ora Fine'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='event_images/', verbose_name='Immagine'),
        ),
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(max_length=255, verbose_name='Luogo'),
        ),
        migrations.AlterField(
            model_name='event',
            name='max_attendees',
            field=models.IntegerField(blank=True, null=True, verbose_name='Numero Massimo Partecipanti'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organized_events', to=settings.AUTH_USER_MODEL, verbose_name='Organizzatore'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(verbose_name='Data e Ora Inizio'),
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('draft', 'Bozza'), ('published', 'Pubblicato'), ('ongoing', 'In Corso'), ('completed', 'Completato'), ('cancelled', 'Annullato')], default='draft', max_length=15, verbose_name='Stato'),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Titolo'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='status',
            field=models.CharField(choices=[('pending', 'In Attesa'), ('confirmed', 'Confermato'), ('cancelled', 'Annullato'), ('attended', 'Partecipato')], default='pending', max_length=15),
        ),
    ]
