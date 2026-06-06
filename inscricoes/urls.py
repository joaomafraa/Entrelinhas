from django.urls import path

from .views import (
    dashboard_admin,
    dashboard_aluna,
    criar_inscricao,
    sucesso,
    listar_produtos,
    criar_produto,
    editar_produto,
    excluir_produto,
    imagem_produto,
    listar_servicos,
    criar_servico,
    editar_servico,
    excluir_servico,
    imagem_servico,
    listar_inscricoes,
    listar_certificados,
    atualizar_status_inscricao,
    confirmar_exclusao_inscricoes,
    excluir_inscricoes,
    detalhes_inscricao,
    editar_matricula,
    cancelar_matricula,
    listar_aulas,
    criar_aula,
    editar_aula,
    confirmar_exclusao_aulas,
    excluir_aulas,
    calendario_aulas,
    registrar_presenca,
    liberar_certificado,
    upload_certificado,
    baixar_certificado,
)

urlpatterns = [

    path(
        'dashboard/',
        dashboard_admin,
        name='dashboard_admin'
    ),

    path(
        'area-aluna/',
        dashboard_aluna,
        name='dashboard_aluna'
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
        'produtos/',
        listar_produtos,
        name='listar_produtos'
    ),

    path(
        'produtos/novo/',
        criar_produto,
        name='criar_produto'
    ),

    path(
        'produtos/<int:id>/editar/',
        editar_produto,
        name='editar_produto'
    ),

    path(
        'produtos/<int:id>/excluir/',
        excluir_produto,
        name='excluir_produto'
    ),

    path(
        'produtos/<int:id>/imagem/',
        imagem_produto,
        name='imagem_produto'
    ),

    path(
        'servicos/',
        listar_servicos,
        name='listar_servicos'
    ),

    path(
        'servicos/novo/',
        criar_servico,
        name='criar_servico'
    ),

    path(
        'servicos/<int:id>/editar/',
        editar_servico,
        name='editar_servico'
    ),

    path(
        'servicos/<int:id>/excluir/',
        excluir_servico,
        name='excluir_servico'
    ),

    path(
        'servicos/<int:id>/imagem/',
        imagem_servico,
        name='imagem_servico'
    ),

    path(
        'certificados/',
        listar_certificados,
        name='listar_certificados'
    ),

    path(
        'inscricoes/<int:id>/status/',
        atualizar_status_inscricao,
        name='atualizar_status_inscricao'
    ),

    path(
        'inscricoes/excluir/',
        excluir_inscricoes,
        name='excluir_inscricoes'
    ),

    path(
        'inscricoes/confirmar-exclusao/',
        confirmar_exclusao_inscricoes,
        name='confirmar_exclusao_inscricoes'
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
        'aulas/excluir/',
        excluir_aulas,
        name='excluir_aulas'
    ),

    path(
        'aulas/confirmar-exclusao/',
        confirmar_exclusao_aulas,
        name='confirmar_exclusao_aulas'
    ),

    path(
        'aulas/<int:id>/presenca/',
        registrar_presenca,
        name='registrar_presenca'
    ),
    
    path(
        'inscricoes/<int:id>/certificado/liberar/',
        liberar_certificado,
        name='liberar_certificado'
    ),

    path(
        'inscricoes/<int:id>/certificado/upload/',
        upload_certificado,
        name='upload_certificado'
    ),

    path(
        'inscricoes/<int:id>/certificado/baixar/',
        baixar_certificado,
        name='baixar_certificado_admin'
    ),

    path(
        'certificado/baixar/',
        baixar_certificado,
        name='baixar_certificado'
    ),

]
