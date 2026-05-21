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
]
