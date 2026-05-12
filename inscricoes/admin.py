from django.contrib import admin
from .models import Inscricao


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'email',
        'cpf',
        'idade',
        'user',
        'disponibilidade',
        'status',
        'ativa',
        'data_criacao',
    )

    search_fields = (
        'nome',
        'email',
        'cpf',
    )

    list_filter = (
        'disponibilidade',
        'status',
        'ativa',
        'data_criacao',
    )
