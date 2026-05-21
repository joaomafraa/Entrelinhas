import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria ou atualiza um superusuario a partir de variaveis de ambiente.'

    def handle(self, *args, **options):

        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        name = os.environ.get('DJANGO_SUPERUSER_NAME', 'Administradora')

        if not email or not password:

            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD nao definidos. Admin nao foi criado.'
                )
            )

            return

        User = get_user_model()
        first_name, _, last_name = name.strip().partition(' ')

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:

            self.stdout.write(self.style.SUCCESS(f'Superusuario {email} criado com sucesso.'))

        else:

            self.stdout.write(self.style.SUCCESS(f'Superusuario {email} atualizado com sucesso.'))
