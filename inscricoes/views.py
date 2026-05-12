from django.shortcuts import render, redirect, get_object_or_404

from .models import Inscricao
from .forms import InscricaoForm


def criar_inscricao(request):

    if request.method == 'POST':

        form = InscricaoForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('sucesso')

    else:

        form = InscricaoForm()

    return render(
        request,
        'inscricoes/inscricao.html',
        {'form': form}
    )


def sucesso(request):

    return render(
        request,
        'inscricoes/sucesso.html'
    )


def listar_inscricoes(request):

    inscricoes = Inscricao.objects.all()

    return render(
        request,
        'inscricoes/listar_inscricoes.html',
        {'inscricoes': inscricoes}
    )


def detalhes_inscricao(request, id):

    inscricao = get_object_or_404(
        Inscricao,
        id=id
    )

    return render(
        request,
        'inscricoes/detalhes.html',
        {'inscricao': inscricao}
    )


def editar_matricula(request, id):

    inscricao = get_object_or_404(
        Inscricao,
        id=id
    )

    if request.method == 'POST':

        form = InscricaoForm(
            request.POST,
            instance=inscricao
        )

        if form.is_valid():

            form.save()

            return redirect('listar_inscricoes')

    else:

        form = InscricaoForm(instance=inscricao)

    return render(
        request,
        'inscricoes/editar_matricula.html',
        {
            'form': form,
            'inscricao': inscricao
        }
    )


def cancelar_matricula(request, id):

    inscricao = get_object_or_404(
        Inscricao,
        id=id
    )

    if request.method == 'POST':

        inscricao.ativa = False

        inscricao.save()

        return redirect('listar_inscricoes')

    return render(
        request,
        'inscricoes/cancelar_matricula.html',
        {'inscricao': inscricao}
    )

def home(request):

    return render(
        request,
        'inscricoes/home.html'
    )