from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Eliminato il'),
        ),
    ]
