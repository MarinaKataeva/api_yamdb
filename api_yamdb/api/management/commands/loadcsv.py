from django.core.management.base import BaseCommand, CommandError
from reviews.models import User, Category, Genre, GenreTitle, Title, Review, Comment


class Command(BaseCommand):
    help = 'Load test data from .csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_filenames', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_filename in options['csv_filenames']:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
