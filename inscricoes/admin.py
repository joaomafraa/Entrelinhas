from django.contrib import admin
from .models import (
    Aula,
    Inscricao,
    Produto,
    ProdutoImagem,
    Servico,
    ServicoImagem,
    SolicitacaoContato,
)


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


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):

    list_display = (
        'data',
        'horario',
        'topico',
        'data_criacao',
    )

    search_fields = (
        'topico',
    )

    list_filter = (
        'data',
        'horario',
    )


class ProdutoImagemInline(admin.TabularInline):

    model = ProdutoImagem
    extra = 0
    fields = (
        'nome',
        'tipo',
        'ordem',
        'criada_em',
    )
    readonly_fields = (
        'criada_em',
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'categoria',
        'preco',
        'whatsapp_contato',
        'ativo',
        'data_criacao',
    )

    search_fields = (
        'nome',
        'categoria',
        'whatsapp_contato',
    )

    list_filter = (
        'categoria',
        'ativo',
    )

    inlines = (
        ProdutoImagemInline,
    )


class ServicoImagemInline(admin.TabularInline):

    model = ServicoImagem
    extra = 0
    fields = (
        'nome',
        'tipo',
        'ordem',
        'criada_em',
    )
    readonly_fields = (
        'criada_em',
    )


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'tipo',
        'whatsapp_contato',
        'ativo',
        'data_criacao',
    )

    search_fields = (
        'nome',
        'tipo',
        'whatsapp_contato',
    )

    list_filter = (
        'tipo',
        'ativo',
    )

    inlines = (
        ServicoImagemInline,
    )

    exclude = (
        'preco',
    )


@admin.register(SolicitacaoContato)
class SolicitacaoContatoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'tipo',
        'email',
        'telefone',
        'status',
        'criada_em',
    )

    search_fields = (
        'nome',
        'email',
        'telefone',
        'mensagem',
    )

    list_filter = (
        'tipo',
        'status',
        'criada_em',
    )

    readonly_fields = (
        'criada_em',
        'atualizada_em',
    )
