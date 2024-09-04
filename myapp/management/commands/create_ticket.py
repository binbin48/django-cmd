from django.core.management.base import BaseCommand
from myapp.models import Ticket
from myapp.utils import chunk_list


class Command(BaseCommand):
    help = "generate tickets"

    def add_arguments(self, parser):
        # Adding batch_size as an optional argument
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,  # Default value if not passed
            help='Number of records to create per batch (default: 10000)'
        )

        parser.add_argument(
            '--total-row',
            type=int,
            default=1_000_000,  # Default value if not passed
            help='Total number of ticket'
        )

    def handle(self, *args, **kwargs):
        needed_rows = kwargs["total_row"]
        exist_ticket_count = Ticket.objects.count()
        batch_size = kwargs["batch_size"]

        for start, end in chunk_list(exist_ticket_count,
                                     needed_rows,
                                     batch_size):
            tickets = [Ticket() for _ in range(start, end)]
            Ticket.objects.bulk_create(tickets, batch_size=len(tickets))

        current_ticket_count = Ticket.objects.count()
        self.stdout.write(f"Created {current_ticket_count - exist_ticket_count} tickets") # noqa
