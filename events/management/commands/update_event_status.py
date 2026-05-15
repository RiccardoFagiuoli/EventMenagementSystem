from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event


class Command(BaseCommand):
    help = 'Aggiorna automaticamente lo stato degli eventi nel database'

    def handle(self, *args, **options):
        now = timezone.now()

        # Statistiche per report
        stats = {
            'ongoing': 0,
            'completed': 0,
        }

        # 1. published → ongoing (eventi iniziati)
        ongoing_events = Event.objects.filter(
            status='published',
            start_date__lte=now,
            end_date__gte=now
        )
        stats['ongoing'] = ongoing_events.update(status='ongoing')

        # 2. ongoing → completed (eventi finiti)
        #    e anche published → completed (se saltano ongoing)
        completed_events = Event.objects.filter(
            status__in=['published', 'ongoing'],  # prende entrambi
            end_date__lte=now
        )
        stats['completed'] = completed_events.update(status='completed')

        # Output nel log di Railway
        total = stats['ongoing'] + stats['completed']

        if total > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Eventi aggiornati: {stats["ongoing"]} → ongoing, '
                    f'{stats["completed"]} → completed'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('⚠️ Nessun evento da aggiornare'))