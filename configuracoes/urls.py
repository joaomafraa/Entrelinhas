from django.contrib import admin
from django.urls import path, include

from inscricoes.views import (
    admin_redirect,
    cadastro,
    home,
    imagem_vitrine_produto,
    imagem_vitrine_servico,
    login_plataforma,
    sair,
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
        'bazar/servico/<int:id>/imagem/',
        imagem_vitrine_servico,
        name='imagem_vitrine_servico'
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
