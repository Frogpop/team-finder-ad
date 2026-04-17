from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает тестовые данные: пользователей, проекты, избранное и участия'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю загрузку тестовых данных...')

        with transaction.atomic():
            users_data = [
                {'email': 'ivan@test.com', 'name': 'Иван', 'surname': 'Петров', 'phone': '+79001112233',
                 'about': 'Python Backend'},
                {'email': 'anna@test.com', 'name': 'Анна', 'surname': 'Сидорова', 'phone': '+79004445566',
                 'about': 'Frontend & Design'},
                {'email': 'max@test.com', 'name': 'Макс', 'surname': 'Волков', 'phone': '+79007778899',
                 'about': 'Fullstack Developer'},
            ]

            users = []

            password = '!@#$%^&*'

            for u_data in users_data:
                user, created = User.objects.get_or_create(email=u_data['email'])
                if created:
                    user.set_password(password)
                    user.name = u_data['name']
                    user.surname = u_data['surname']
                    user.phone = u_data['phone']
                    user.about = u_data['about']
                    user.save()
                users.append(user)
            self.stdout.write(
                self.style.SUCCESS(f'Пользователи готовы (всего: {len(users)}). Пароль для всех: `!@#$%^&*`'))

            projects_data = [
                {'name': 'Django E-Commerce', 'owner': users[0], 'desc': 'Магазин на Django + HTMX'},
                {'name': 'React Dashboard', 'owner': users[1], 'desc': 'Панель аналитики для бизнеса'},
                {'name': 'Telegram Bot', 'owner': users[2], 'desc': 'Бот для трекинга задач'},
            ]

            for p_data in projects_data:
                proj, created = Project.objects.get_or_create(
                    name=p_data['name'], owner=p_data['owner'],
                    defaults={'description': p_data['desc'], 'status': 'open'}
                )
                if created:
                    proj.participants.add(p_data['owner'])
            self.stdout.write(self.style.SUCCESS('Проекты созданы'))

            p1 = Project.objects.get(name='Django E-Commerce')
            p2 = Project.objects.get(name='React Dashboard')

            # Анна добавила проект Ивана в избранное фильтр "Пользователи, которым нравятся мои проекты"
            users[1].favorites.add(p1)

            # Макс участвует в проекте Ивана фильтр "Участники моих проектов"
            p1.participants.add(users[2])

            # Макс участвует в проекте Анныфильтр "Авторы проектов, в которых я участвую"
            p2.participants.add(users[2])

            self.stdout.write(self.style.SUCCESS('Связи для фильтров настроены'))
            self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены!'))
