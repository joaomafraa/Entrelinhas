from django.contrib import admin
from django.urls import path, include

from inscricoes.views import admin_redirect, cadastro, home, login_plataforma, sair


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
        'sair/',
        sair,
        name='sair'
    ),

    path(
        'inscricao/',
        include('inscricoes.urls')
    ),
]
