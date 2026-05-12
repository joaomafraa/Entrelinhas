from django.contrib import admin
from django.urls import path, include

from inscricoes.views import home


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        home,
        name='home'
    ),

    path(
        'inscricao/',
        include('inscricoes.urls')
    ),
]