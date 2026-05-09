from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.criar_inscricao,
        name='criar_inscricao'
    ),

    path(
        'sucesso/',
        views.sucesso,
        name='sucesso'
    ),

    path(
        'inscricoes/',
        views.listar_inscricoes,
        name='listar_inscricoes'
    ),

    path(
        'inscricao/<int:id>/',
        views.detalhes_inscricao,
        name='detalhes_inscricao'
    ),

    path(
        'editar/<int:id>/',
        views.editar_matricula,
        name='editar_matricula'
    ),

    path(
        'cancelar/<int:id>/',
        views.cancelar_matricula,
        name='cancelar_matricula'
    ),
]