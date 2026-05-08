from django.db import models

# Create your models here.

from django.db import models


class Inscricao(models.Model):

    DISPONIBILIDADE = (
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    )

    nome = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
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

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nome