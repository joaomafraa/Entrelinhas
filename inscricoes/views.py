from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CadastroForm, InscricaoForm, LoginForm, normalizar_cpf
from .models import Inscricao


def _inscricoes_do_usuario(user):

    if user.is_staff:

        return Inscricao.objects.all()

    return Inscricao.objects.filter(user=user)


def home(request):

    return render(
        request,
        'inscricoes/home.html'
    )


def login_plataforma(request):

    if request.user.is_authenticated:

        return redirect('listar_inscricoes')

    if request.method == 'POST':

        form = LoginForm(request, request.POST)

        if form.is_valid():

            login(request, form.user)

            return redirect('listar_inscricoes')

    else:

        form = LoginForm(request)

    return render(
        request,
        'inscricoes/login.html',
        {'form': form}
    )


def cadastro(request):

    if request.user.is_authenticated:

        return redirect('criar_inscricao')

    if request.method == 'POST':

        form = CadastroForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('criar_inscricao')

    else:

        form = CadastroForm()

    return render(
        request,
        'inscricoes/cadastro.html',
        {'form': form}
    )


def sair(request):

    logout(request)

    return redirect('home')


@login_required
def criar_inscricao(request):

    inscricao_existente = (
        Inscricao.objects.filter(user=request.user).first()
        or Inscricao.objects.filter(email=request.user.email).first()
    )

    if request.method == 'POST':

        form = InscricaoForm(
            request.POST,
            instance=inscricao_existente
        )

        if form.is_valid():

            inscricao = form.save(commit=False)
            inscricao.user = request.user
            inscricao.email = request.user.email
            inscricao.save()

            return redirect('sucesso')

    else:

        initial = {
            'nome': request.user.get_full_name() or request.user.username
        }

        form = InscricaoForm(
            instance=inscricao_existente,
            initial=initial
        )

    return render(
        request,
        'inscricoes/inscricao.html',
        {'form': form}
    )


@login_required
def sucesso(request):

    inscricao = _inscricoes_do_usuario(request.user).order_by('-data_criacao').first()

    return render(
        request,
        'inscricoes/sucesso.html',
        {'inscricao': inscricao}
    )


@login_required
def listar_inscricoes(request):

    inscricoes = _inscricoes_do_usuario(request.user)

    if request.user.is_staff:

        q = request.GET.get('q', '').strip()

        if q:

            cpf = normalizar_cpf(q)
            filtros = Q(nome__icontains=q) | Q(email__icontains=q)

            if cpf:

                filtros |= Q(cpf__icontains=cpf)

            if q.isdigit():

                filtros |= Q(id=int(q))

            inscricoes = inscricoes.filter(filtros)

        inscricoes = inscricoes.order_by('-data_criacao')
        paginator = Paginator(inscricoes, 6)
        page_obj = paginator.get_page(request.GET.get('page'))

        return render(
            request,
            'inscricoes/listar_inscricoes.html',
            {
                'inscricoes': page_obj.object_list,
                'is_admin_list': True,
                'page_obj': page_obj,
                'q': q,
                'total_count': paginator.count,
                'start_index': page_obj.start_index() if paginator.count else 0,
                'end_index': page_obj.end_index() if paginator.count else 0,
            }
        )

    return render(
        request,
        'inscricoes/listar_inscricoes.html',
        {'inscricoes': inscricoes}
    )


@login_required
def detalhes_inscricao(request, id):

    inscricao = get_object_or_404(
        _inscricoes_do_usuario(request.user),
        id=id
    )

    return render(
        request,
        'inscricoes/detalhes.html',
        {'inscricao': inscricao}
    )


@login_required
def editar_matricula(request, id):

    inscricao = get_object_or_404(
        _inscricoes_do_usuario(request.user),
        id=id
    )

    if request.method == 'POST':

        form = InscricaoForm(
            request.POST,
            instance=inscricao
        )

        if form.is_valid():

            inscricao = form.save(commit=False)

            if inscricao.user:

                inscricao.email = inscricao.user.email

            inscricao.save()

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


@login_required
def cancelar_matricula(request, id):

    inscricao = get_object_or_404(
        _inscricoes_do_usuario(request.user),
        id=id
    )

    if request.method == 'POST':

        inscricao.delete()

        messages.success(
            request,
            'Sua inscrição no curso Costurando Sonhos foi cancelada e removida da plataforma. Quando quiser, você poderá realizar uma nova inscrição.'
        )

        return redirect('listar_inscricoes')

    return render(
        request,
        'inscricoes/cancelar_matricula.html',
        {'inscricao': inscricao}
    )
