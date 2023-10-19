import csv

from django.core.management.base import BaseCommand, CommandError

from api_yamdb.settings import BASE_DIR
from reviews.models import (
    User, Category, Genre, GenreTitle, Title, Review, Comment
)

TEST_DATA = {
    'users': 'users.csv',
    'category': 'category.csv',
    'genre': 'genre.csv',
    'titles': 'titles.csv',
    'genre_title': 'genre_title.csv',
    'review': 'review.csv',
    'comments': 'comments.csv',
}


class Command(BaseCommand):
    help = 'Load test data from .csv file'

    def load_csv(self, filename, table_name):
        if table_name == 'users':
            model = User
            label = "Пользователь"
        elif table_name == 'category':
            model = Category
            label = "Категория"
        elif table_name == 'genre':
            model = Genre
            label = "Жанр"
        elif table_name == 'titles':
            model = Title
            label = "Произведение"
        elif table_name == 'genre_title':
            model = GenreTitle
            label = "Жанр-Произведение"
        elif table_name == 'review':
            model = Review
            label = "Отзыв"
        elif table_name == 'comments':
            model = Comment
            label = "Комментарий"
        else:
            raise KeyError(f'Неизвестное имя таблицы {table_name}')
        with open(filename, 'r', newline='') as csvfile:
            data_fields = next(csvfile).replace(
                '\r', '').replace('\n', '').replace(
                    '^category$', 'category_id').replace(
                        '^author$', 'author_id').replace(
                            '^title$', 'title_id'
            ).split(',')
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                data_obj = dict(zip(data_fields, row))
                model.objects.create(**data_obj)
                print(f'Объект {label} = {data_obj} успешно создан!')

    def add_arguments(self, parser):
        parser.add_argument('csv_dir', nargs='+', type=str)

    def handle(self, *args, **options):
        csv_dirs = options['csv_dir']
        try:
            for csv_dir in csv_dirs:
                for test_data_table in TEST_DATA:
                    test_data_file = TEST_DATA[test_data_table]
                    csv_path = (str(BASE_DIR)
                                + '/' + csv_dir
                                + '/' + test_data_file)
                    self.load_csv(csv_path, test_data_table)
        except CommandError:
            raise CommandError('Ошибка при загрузке данных'
                               f'из файлов csv в каталоге {csv_dir}!')
