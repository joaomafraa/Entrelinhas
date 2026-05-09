from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Inscricao


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'email',
        'disponibilidade',
        'ativa',
        'data_criacao',
    )

    search_fields = (
        'nome',
        'email',
    )

    list_filter = (
        'disponibilidade',
        'ativa',
        'data_criacao',
    )