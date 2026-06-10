from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_description_alter_event_end_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-start_date'], 'permissions': [('can_create_event', 'Può creare eventi'), ('can_edit_own_events', 'Può modificare i propri eventi'), ('can_delete_own_events', 'Può eliminare i propri eventi'), ('can_view_attendees', 'Può visualizzare la lista dei partecipanti')]},
        ),
    ]
