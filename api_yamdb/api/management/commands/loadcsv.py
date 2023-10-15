from django.core.management.base import BaseCommand, CommandError
# from reviews.models import User, Category, Genre, GenreTitle, Title, Review, Comment


class Command(BaseCommand):
    help = 'Load test data from .csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_filenames', nargs='+', type=str)
