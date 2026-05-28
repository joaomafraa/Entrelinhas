import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AulaForm, CadastroForm, InscricaoForm, LoginForm, normalizar_cpf
from .models import Aula, Inscricao, Presenca


MESES = [
    '',
    'Janeiro',
    'Fevereiro',
    'Marco',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
]


def _inscricoes_do_usuario(user):

    if user.is_staff:

        return Inscricao.objects.all()

    return Inscricao.objects.filter(user=user)


def home(request):

    if request.user.is_authenticated and request.user.is_staff:

        return redirect('dashboard_admin')

    return render(
        request,
        'inscricoes/home.html'
    )


def login_plataforma(request):

    if request.user.is_authenticated:

        if request.user.is_staff:

            return redirect('dashboard_admin')

        return redirect('listar_inscricoes')

    if request.method == 'POST':

        form = LoginForm(request, request.POST)

        if form.is_valid():

            login(request, form.user)

            if form.user.is_staff:

                return redirect('dashboard_admin')

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


def admin_redirect(request):

    if request.user.is_authenticated:

        if request.user.is_staff:

            return redirect('dashboard_admin')

        return redirect('listar_inscricoes')

    return redirect('login')


@login_required
def dashboard_admin(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    total_inscricoes = Inscricao.objects.count()

    return render(
        request,
        'inscricoes/dashboard_admin.html',
        {
            'current_admin_page': 'overview',
            'total_inscricoes': total_inscricoes,
            'total_pendentes': Inscricao.objects.filter(status='pendente').count(),
            'total_aprovadas': Inscricao.objects.filter(status='aprovada').count(),
            'total_recusadas': Inscricao.objects.filter(status='recusada').count(),
            'total_aulas': Aula.objects.count(),
        }
    )


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

            messages.success(
                request,
                'Inscricao registrada com sucesso. Voce ja pode acompanhar sua matricula pela plataforma.'
            )

            return redirect('sucesso')

        messages.warning(
            request,
            'Nao foi possivel concluir a inscricao. Revise os campos destacados e tente novamente.'
        )

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
                'base_template': 'inscricoes/admin_base.html',
                'current_admin_page': 'inscricoes',
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
@require_POST
def excluir_inscricoes(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    ids = request.POST.getlist('inscricoes_selecionadas')

    if not ids:

        messages.warning(
            request,
            'Selecione pelo menos uma inscricao para excluir.'
        )

        return redirect('listar_inscricoes')

    total_excluido, _ = Inscricao.objects.filter(id__in=ids).delete()

    messages.success(
        request,
        f'{total_excluido} inscricao(oes) excluida(s) com sucesso.'
    )

    return redirect('listar_inscricoes')


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

            messages.success(
                request,
                'Matricula atualizada com sucesso.'
            )

            return redirect('listar_inscricoes')

        messages.warning(
            request,
            'Nao foi possivel salvar as alteracoes. Revise os campos destacados e tente novamente.'
        )

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


@login_required
def listar_aulas(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    aulas = Aula.objects.all()

    paginator = Paginator(aulas, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'inscricoes/listar_aulas.html',
        {
            'aulas': page_obj.object_list,
            'current_admin_page': 'aulas',
            'page_obj': page_obj,
            'total_count': paginator.count,
            'start_index': page_obj.start_index() if paginator.count else 0,
            'end_index': page_obj.end_index() if paginator.count else 0,
        }
    )


@login_required
def criar_aula(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    if request.method == 'POST':

        form = AulaForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Aula criada com sucesso.'
            )

            return redirect('listar_aulas')

        messages.warning(
            request,
            'Nao foi possivel criar a aula. Revise os campos destacados e tente novamente.'
        )

    else:

        form = AulaForm()

    return render(
        request,
        'inscricoes/criar_aula.html',
        {
            'form': form,
            'current_admin_page': 'aulas',
            'titulo': 'Nova aula',
            'descricao': 'Cadastre uma aula para depois registrar a presenca das alunas.',
            'texto_botao': 'Criar aula',
        }
    )


@login_required
def editar_aula(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    aula = get_object_or_404(Aula, id=id)

    if request.method == 'POST':

        form = AulaForm(request.POST, instance=aula)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Aula atualizada com sucesso.'
            )

            return redirect('listar_aulas')

        messages.warning(
            request,
            'Nao foi possivel atualizar a aula. Revise os campos destacados e tente novamente.'
        )

    else:

        form = AulaForm(instance=aula)

    return render(
        request,
        'inscricoes/criar_aula.html',
        {
            'form': form,
            'aula': aula,
            'current_admin_page': 'aulas',
            'titulo': 'Editar aula',
            'descricao': 'Atualize a data, o horario e o topico da aula.',
            'texto_botao': 'Salvar alteracoes',
        }
    )


@login_required
def calendario_aulas(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    hoje = date.today()

    try:

        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))

        if mes < 1 or mes > 12:

            raise ValueError

    except (TypeError, ValueError):

        ano = hoje.year
        mes = hoje.month

    primeiro_dia = date(ano, mes, 1)
    _, ultimo_dia = calendar.monthrange(ano, mes)

    if mes == 1:

        mes_anterior = {'ano': ano - 1, 'mes': 12}

    else:

        mes_anterior = {'ano': ano, 'mes': mes - 1}

    if mes == 12:

        proximo_mes = {'ano': ano + 1, 'mes': 1}

    else:

        proximo_mes = {'ano': ano, 'mes': mes + 1}

    aulas = Aula.objects.filter(
        data__year=ano,
        data__month=mes
    ).order_by('data', 'horario')

    aulas_por_dia = {}

    for aula in aulas:

        aulas_por_dia.setdefault(aula.data.day, []).append(aula)

    semanas = []

    for semana in calendar.Calendar(firstweekday=6).monthdayscalendar(ano, mes):

        semanas.append([
            {
                'numero': dia,
                'data': date(ano, mes, dia) if dia else None,
                'aulas': aulas_por_dia.get(dia, []),
                'is_today': dia != 0 and date(ano, mes, dia) == hoje,
            }
            for dia in semana
        ])

    return render(
        request,
        'inscricoes/calendario_aulas.html',
        {
            'current_admin_page': 'aulas',
            'semanas': semanas,
            'nome_mes': MESES[mes],
            'ano': ano,
            'mes': mes,
            'mes_anterior': mes_anterior,
            'proximo_mes': proximo_mes,
            'total_aulas_mes': aulas.count(),
            'primeiro_dia': primeiro_dia,
            'ultimo_dia': date(ano, mes, ultimo_dia),
        }
    )


@login_required
def registrar_presenca(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    aula = get_object_or_404(Aula, id=id)

    if request.method == 'POST':

        alunas_aprovadas = Inscricao.objects.filter(status='aprovada')

        for inscricao in alunas_aprovadas:

            marcou = request.POST.get(f'presente_{inscricao.id}') == 'on'

            Presenca.objects.update_or_create(
                aula=aula,
                inscricao=inscricao,
                defaults={'presente': marcou}
            )

        messages.success(
            request,
            'Presencas registradas com sucesso.'
        )

        return redirect('registrar_presenca', id=aula.id)

    alunas_aprovadas = Inscricao.objects.filter(status='aprovada').order_by('nome')

    presencas_por_inscricao = {
        presenca.inscricao_id: presenca.presente
        for presenca in Presenca.objects.filter(aula=aula)
    }

    alunas = [
        (aluna, presencas_por_inscricao.get(aluna.id, False))
        for aluna in alunas_aprovadas
    ]

    return render(
        request,
        'inscricoes/registrar_presenca.html',
        {
            'aula': aula,
            'alunas': alunas,
            'current_admin_page': 'aulas',
        }
    )
