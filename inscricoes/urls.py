from django.urls import path

from .views import (
    criar_inscricao,
    sucesso,
    listar_inscricoes,
    detalhes_inscricao,
    editar_matricula,
    cancelar_matricula,
)

urlpatterns = [

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