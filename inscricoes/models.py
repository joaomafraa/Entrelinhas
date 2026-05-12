from django.conf import settings
from django.db import models
from django.utils import timezone


class Inscricao(models.Model):

    DISPONIBILIDADE = (
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    )

    STATUS = (
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscricoes',
        blank=True,
        null=True
    )

    nome = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    cpf = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True
    )

    data_nascimento = models.DateField(
        blank=True,
        null=True
    )

    telefone = models.CharField(
        max_length=20
    )

    disponibilidade = models.CharField(
        max_length=20,
        choices=DISPONIBILIDADE
    )

    observacoes = models.TextField(
        blank=True,
        null=True
    )

    ativa = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pendente'
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def idade(self):

        if not self.data_nascimento:

            return None

        hoje = timezone.localdate()

        return (
            hoje.year
            - self.data_nascimento.year
            - (
                (hoje.month, hoje.day)
                < (self.data_nascimento.month, self.data_nascimento.day)
            )
        )

    @property
    def cpf_formatado(self):

        if not self.cpf or len(self.cpf) != 11:

            return self.cpf or ''

        return f'{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}'

    def __str__(self):
        return self.nome
