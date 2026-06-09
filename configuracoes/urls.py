from django.contrib import admin
from django.urls import path, include

from inscricoes.views import (
    admin_redirect,
    cadastro,
    chat_suporte,
    contato,
    home,
    detalhe_vitrine_produto,
    detalhe_vitrine_servico,
    imagem_vitrine_produto_galeria,
    imagem_vitrine_servico_galeria,
    imagem_vitrine_produto,
    imagem_vitrine_servico,
    login_plataforma,
    sair,
    suporte,
    vitrine,
)


urlpatterns = [

    path(
        'admin/',
        admin_redirect,
        name='admin_redirect'
    ),

    path(
        'django-admin/',
        admin.site.urls
    ),

    path(
        '',
        home,
        name='home'
    ),

    path(
        'login/',
        login_plataforma,
        name='login'
    ),

    path(
        'cadastro/',
        cadastro,
        name='cadastro'
    ),

    path(
        'contato/',
        contato,
        name='contato'
    ),

    path(
        'suporte/',
        suporte,
        name='suporte'
    ),

    path(
        'api/chat/',
        chat_suporte,
        name='chat_suporte'
    ),

    path(
        'bazar/',
        vitrine,
        name='vitrine'
    ),

    path(
        'bazar/produto/<int:id>/imagem/',
        imagem_vitrine_produto,
        name='imagem_vitrine_produto'
    ),

    path(
        'bazar/produto/<int:id>/',
        detalhe_vitrine_produto,
        name='detalhe_vitrine_produto'
    ),

    path(
        'bazar/produto/foto/<int:id>/',
        imagem_vitrine_produto_galeria,
        name='imagem_vitrine_produto_galeria'
    ),

    path(
        'bazar/servico/<int:id>/imagem/',
        imagem_vitrine_servico,
        name='imagem_vitrine_servico'
    ),

    path(
        'bazar/servico/<int:id>/',
        detalhe_vitrine_servico,
        name='detalhe_vitrine_servico'
    ),

    path(
        'bazar/servico/foto/<int:id>/',
        imagem_vitrine_servico_galeria,
        name='imagem_vitrine_servico_galeria'
    ),

    path(
        'sair/',
        sair,
        name='sair'
    ),

    path(
        'inscricao/',
        include('inscricoes.urls')
    ),
]
