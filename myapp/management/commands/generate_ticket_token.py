import uuid
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import Ticket
from django.utils import timezone
from datetime import timedelta
from myapp.utils import chunk_list
import os

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Regenerate unique UUIDs for each Ticket's token field"

    def add_arguments(self, parser):
        # Adding batch_size as an optional argument
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,  # Default value if not passed
            help='Number of records to create per batch (default: 10000)'
        )

    def handle(self, *args, **kwargs):
        cmd_start_at = time.time()
        start_row, accumulated_ticket, accumulated_time = self._get_checkpoint()
        total_ticket = Ticket.objects.count()
        self.stdout.write(f"We have totally {total_ticket} tickets. Start from {start_row}")

        if total_ticket == 0 or total_ticket == accumulated_ticket:
            self.stdout.write(self.style.WARNING('No ticket need to be processed.'))
            return

        batch_size = kwargs["batch_size"]

        for start, end in chunk_list(start_row,
                                     total_ticket,
                                     batch_size):
            with transaction.atomic():
                try:
                    start_time = time.time()
                    tickets = Ticket.objects.all().order_by("id")[start: end]
                    for t in tickets:
                        t.token = str(uuid.uuid4())
                    accumulated_ticket += Ticket.objects.bulk_update(
                        tickets,
                        fields=["token"],
                        batch_size=end-start
                    )
                    accumulated_time += time.time() - start_time
                except Exception as e:
                    self.stdout.write("Oops, view log to check the detail error.")
                    logger.exception(e)
                    raise

            self._save_checkpoint(
                end,
                accumulated_ticket,
                accumulated_time
            )
            self._show_progress(total_ticket, accumulated_ticket, accumulated_time)

        cmd_end_at = time.time()
        self.stdout.write(f"Cmd running time: {cmd_end_at - cmd_start_at} seconds ")

    def _get_checkpoint(self):
        try:
            with open("checkpoint.txt", "r") as f:
                ticket_id = int(f.readline())
                proccessed_row = int(f.readline())
                processed_time = float(f.readline())
                return ticket_id, proccessed_row, processed_time
        except FileNotFoundError:
            return 0, 0, 0

    def _save_checkpoint(self, ticket_id, processed_ticket, processed_time):
        with open("checkpoint.txt", "w") as f:
            f.write(str(ticket_id) + os.linesep)
            f.write(str(processed_ticket) + os.linesep)
            f.write(str(processed_time) + os.linesep)

    def _show_progress(self, total_ticket, processed_ticket, processed_time):
        remaining_time = (total_ticket - processed_ticket) * (processed_time / processed_ticket)  # noqa
        eta = timezone.now() + timedelta(seconds=remaining_time)
        self.stdout.write(f"Processed {processed_ticket}/{total_ticket} records. Estimated time remaining: {remaining_time // 60:.0f} minutes. ETA: {eta}.")  # noqa
