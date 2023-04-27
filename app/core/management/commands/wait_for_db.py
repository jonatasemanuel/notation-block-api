"""
Django command to wait for the database to available.
"""
import time

from django.db.utils import OperationError
from django.core.management.base import BaseCommand

from pyscopg2 import OperationalError as Pyscopg2OpError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Pyscopg2OpError, OperationError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SECCESS('Database available!'))
