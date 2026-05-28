from django.urls import path

from .views import (
    dashboard_admin,
    criar_inscricao,
    sucesso,
    listar_inscricoes,
    excluir_inscricoes,
    detalhes_inscricao,
    editar_matricula,
    cancelar_matricula,
    listar_aulas,
    criar_aula,
    editar_aula,
    calendario_aulas,
    registrar_presenca,
)

urlpatterns = [

    path(
        'dashboard/',
        dashboard_admin,
        name='dashboard_admin'
    ),

    path(
        '',
        criar_inscricao,
        name='criar_inscricao'
    ),

    path(
        'sucesso/',
        sucesso,
        name='sucesso'
    ),

    path(
        'inscricoes/',
        listar_inscricoes,
        name='listar_inscricoes'
    ),

    path(
        'inscricoes/excluir/',
        excluir_inscricoes,
        name='excluir_inscricoes'
    ),

    path(
        'inscricao/<int:id>/',
        detalhes_inscricao,
        name='detalhes_inscricao'
    ),

    path(
        'editar/<int:id>/',
        editar_matricula,
        name='editar_matricula'
    ),

    path(
        'cancelar/<int:id>/',
        cancelar_matricula,
        name='cancelar_matricula'
    ),

    path(
        'aulas/',
        listar_aulas,
        name='listar_aulas'
    ),

    path(
        'aulas/nova/',
        criar_aula,
        name='criar_aula'
    ),

    path(
        'aulas/calendario/',
        calendario_aulas,
        name='calendario_aulas'
    ),

    path(
        'aulas/<int:id>/editar/',
        editar_aula,
        name='editar_aula'
    ),

    path(
        'aulas/<int:id>/presenca/',
        registrar_presenca,
        name='registrar_presenca'
    ),
]
