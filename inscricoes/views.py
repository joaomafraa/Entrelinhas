import calendar
import mimetypes
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    AdminInscricaoForm,
    AulaForm,
    ProdutoForm,
    CadastroForm,
    CertificadoUploadForm,
    InscricaoForm,
    LoginForm,
    ServicoForm,
    normalizar_cpf,
)
from .models import Aula, Inscricao, Presenca, Produto, ProdutoImagem, Servico, ServicoImagem


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


def _inscricao_aprovada_do_usuario(user):

    filtros = Q(user=user)

    if user.email:

        filtros |= Q(email=user.email)

    return Inscricao.objects.filter(
        filtros,
        status='aprovada'
    ).order_by('-data_criacao').first()


def _parametros_calendario(request):

    hoje = date.today()

    try:

        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))

        if mes < 1 or mes > 12:

            raise ValueError

    except (TypeError, ValueError):

        ano = hoje.year
        mes = hoje.month

    if mes == 1:

        mes_anterior = {'ano': ano - 1, 'mes': 12}

    else:

        mes_anterior = {'ano': ano, 'mes': mes - 1}

    if mes == 12:

        proximo_mes = {'ano': ano + 1, 'mes': 1}

    else:

        proximo_mes = {'ano': ano, 'mes': mes + 1}

    return hoje, ano, mes, mes_anterior, proximo_mes


def _semanas_do_calendario(ano, mes, hoje):

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

    return semanas, aulas


def _salvar_imagens_bazar(item, imagens, imagem_model, campo_item):

    if not imagens:

        return

    ordem_inicial = item.imagens.count()

    for indice, imagem in enumerate(imagens, start=ordem_inicial):

        imagem_model.objects.create(
            **{
                campo_item: item,
                'nome': imagem.name,
                'tipo': imagem.content_type or '',
                'conteudo': imagem.read(),
                'ordem': indice,
            }
        )


def home(request):

    return render(
        request,
        'inscricoes/home.html'
    )


def login_plataforma(request):

    if request.user.is_authenticated:

        return redirect('home')

    if request.method == 'POST':

        form = LoginForm(request, request.POST)

        if form.is_valid():

            login(request, form.user)

            return redirect('home')

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

        if _inscricao_aprovada_do_usuario(request.user):

            return redirect('dashboard_aluna')

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
            'total_produtos': Produto.objects.count(),
            'total_servicos': Servico.objects.count(),
        }
    )


@login_required
def listar_produtos(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    produtos = Produto.objects.all()
    paginator = Paginator(produtos, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    for produto in page_obj.object_list:

        produto.etiqueta_bazar = produto.categoria
        produto.mostrar_preco_bazar = True

    return render(
        request,
        'bazar/admin/listar.html',
        {
            'current_admin_page': 'produtos',
            'titulo': 'Produtos',
            'descricao': 'Gerencie os produtos disponiveis no bazar.',
            'contador': f'{paginator.count} produto(s) cadastrado(s)',
            'novo_label': 'Novo produto',
            'novo_url': 'criar_produto',
            'editar_url': 'editar_produto',
            'excluir_url': 'excluir_produto',
            'imagem_url': 'imagem_produto',
            'itens': page_obj.object_list,
            'empty_text': 'Nenhum produto cadastrado.',
            'page_obj': page_obj,
            'total_count': paginator.count,
            'start_index': page_obj.start_index() if paginator.count else 0,
            'end_index': page_obj.end_index() if paginator.count else 0,
        }
    )


@login_required
def criar_produto(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    if request.method == 'POST':

        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():

            produto = form.save(commit=False)
            produto.save()
            _salvar_imagens_bazar(
                produto,
                form.cleaned_data.get('imagem'),
                ProdutoImagem,
                'produto'
            )
            messages.success(request, 'Produto cadastrado com sucesso.')

            return redirect('listar_produtos')

        messages.warning(request, 'Nao foi possivel cadastrar o produto. Revise os campos destacados.')

    else:

        form = ProdutoForm()

    return render(
        request,
        'bazar/admin/form.html',
        {
            'current_admin_page': 'produtos',
            'titulo': 'Novo produto',
            'descricao': 'Cadastre nome, descricao, valor, categoria e imagem do produto.',
            'form': form,
            'back_url': 'listar_produtos',
            'texto_botao': 'Salvar produto',
        }
    )


@login_required
def editar_produto(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    produto = get_object_or_404(Produto, id=id)

    if request.method == 'POST':

        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():

            produto = form.save(commit=False)
            produto.save()
            _salvar_imagens_bazar(
                produto,
                form.cleaned_data.get('imagem'),
                ProdutoImagem,
                'produto'
            )
            messages.success(request, 'Produto atualizado com sucesso.')

            return redirect('listar_produtos')

        messages.warning(request, 'Nao foi possivel atualizar o produto. Revise os campos destacados.')

    else:

        form = ProdutoForm(instance=produto)

    return render(
        request,
        'bazar/admin/form.html',
        {
            'current_admin_page': 'produtos',
            'titulo': 'Editar produto',
            'descricao': 'Atualize as informacoes do produto.',
            'form': form,
            'back_url': 'listar_produtos',
            'texto_botao': 'Salvar alteracoes',
            'item': produto,
            'imagem_url': 'imagem_produto',
        }
    )


@login_required
@require_POST
def excluir_produto(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    messages.success(request, 'Produto excluido com sucesso.')

    return redirect('listar_produtos')


@login_required
def imagem_produto(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    produto = get_object_or_404(Produto, id=id)

    if not produto.tem_imagem:

        return HttpResponse(status=404)

    imagem = produto.imagem_capa

    if imagem:

        return HttpResponse(
            bytes(imagem.conteudo),
            content_type=imagem.tipo or 'application/octet-stream'
        )

    return HttpResponse(
        bytes(produto.imagem_conteudo),
        content_type=produto.imagem_tipo or 'application/octet-stream'
    )


@login_required
def listar_servicos(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    servicos = Servico.objects.all()
    paginator = Paginator(servicos, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    for servico in page_obj.object_list:

        servico.etiqueta_bazar = servico.tipo
        servico.mostrar_preco_bazar = False

    return render(
        request,
        'bazar/admin/listar.html',
        {
            'current_admin_page': 'servicos',
            'titulo': 'Servicos',
            'descricao': 'Gerencie os servicos oferecidos pelo bazar.',
            'contador': f'{paginator.count} servico(s) cadastrado(s)',
            'novo_label': 'Novo servico',
            'novo_url': 'criar_servico',
            'editar_url': 'editar_servico',
            'excluir_url': 'excluir_servico',
            'imagem_url': 'imagem_servico',
            'itens': page_obj.object_list,
            'empty_text': 'Nenhum servico cadastrado.',
            'page_obj': page_obj,
            'total_count': paginator.count,
            'start_index': page_obj.start_index() if paginator.count else 0,
            'end_index': page_obj.end_index() if paginator.count else 0,
        }
    )


@login_required
def criar_servico(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    if request.method == 'POST':

        form = ServicoForm(request.POST, request.FILES)

        if form.is_valid():

            servico = form.save(commit=False)
            servico.save()
            _salvar_imagens_bazar(
                servico,
                form.cleaned_data.get('imagem'),
                ServicoImagem,
                'servico'
            )
            messages.success(request, 'Servico cadastrado com sucesso.')

            return redirect('listar_servicos')

        messages.warning(request, 'Nao foi possivel cadastrar o servico. Revise os campos destacados.')

    else:

        form = ServicoForm()

    return render(
        request,
        'bazar/admin/form.html',
        {
            'current_admin_page': 'servicos',
            'titulo': 'Novo servico',
            'descricao': 'Cadastre nome, descricao, tipo e imagem do servico.',
            'form': form,
            'back_url': 'listar_servicos',
            'texto_botao': 'Salvar servico',
        }
    )


@login_required
def editar_servico(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    servico = get_object_or_404(Servico, id=id)

    if request.method == 'POST':

        form = ServicoForm(request.POST, request.FILES, instance=servico)

        if form.is_valid():

            servico = form.save(commit=False)
            servico.save()
            _salvar_imagens_bazar(
                servico,
                form.cleaned_data.get('imagem'),
                ServicoImagem,
                'servico'
            )
            messages.success(request, 'Servico atualizado com sucesso.')

            return redirect('listar_servicos')

        messages.warning(request, 'Nao foi possivel atualizar o servico. Revise os campos destacados.')

    else:

        form = ServicoForm(instance=servico)

    return render(
        request,
        'bazar/admin/form.html',
        {
            'current_admin_page': 'servicos',
            'titulo': 'Editar servico',
            'descricao': 'Atualize as informacoes do servico.',
            'form': form,
            'back_url': 'listar_servicos',
            'texto_botao': 'Salvar alteracoes',
            'item': servico,
            'imagem_url': 'imagem_servico',
        }
    )


@login_required
@require_POST
def excluir_servico(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    servico = get_object_or_404(Servico, id=id)
    servico.delete()
    messages.success(request, 'Servico excluido com sucesso.')

    return redirect('listar_servicos')


@login_required
def imagem_servico(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    servico = get_object_or_404(Servico, id=id)

    if not servico.tem_imagem:

        return HttpResponse(status=404)

    imagem = servico.imagem_capa

    if imagem:

        return HttpResponse(
            bytes(imagem.conteudo),
            content_type=imagem.tipo or 'application/octet-stream'
        )

    return HttpResponse(
        bytes(servico.imagem_conteudo),
        content_type=servico.imagem_tipo or 'application/octet-stream'
    )


@login_required
def listar_certificados(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    inscricoes = Inscricao.objects.filter(
        status='aprovada'
    ).order_by('nome')
    paginator = Paginator(inscricoes, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'certificados/admin/listar.html',
        {
            'current_admin_page': 'certificados',
            'inscricoes': page_obj.object_list,
            'page_obj': page_obj,
            'total_count': paginator.count,
            'start_index': page_obj.start_index() if paginator.count else 0,
            'end_index': page_obj.end_index() if paginator.count else 0,
        }
    )


@login_required
def dashboard_aluna(request):

    if request.user.is_staff:

        return redirect('dashboard_admin')

    inscricao = _inscricao_aprovada_do_usuario(request.user)

    if not inscricao:

        return redirect('listar_inscricoes')

    abas_validas = {'visao-geral', 'frequencia', 'perfil', 'certificados'}
    aba_ativa = request.GET.get('aba', 'visao-geral')

    if aba_ativa not in abas_validas:

        aba_ativa = 'visao-geral'

    hoje = date.today()
    presencas = Presenca.objects.filter(
        inscricao=inscricao,
        aula__data__lte=hoje
    )
    aulas_registradas = presencas.count()
    presencas_confirmadas = presencas.filter(presente=True).count()
    faltas = presencas.filter(presente=False).count()
    frequencia = round((presencas_confirmadas / aulas_registradas) * 100) if aulas_registradas else 0

    contexto = {
        'inscricao': inscricao,
        'aba_ativa': aba_ativa,
        'aulas_registradas': aulas_registradas,
        'presencas_confirmadas': presencas_confirmadas,
        'faltas': faltas,
        'frequencia': frequencia,
        'curso_concluido': inscricao.concluiu_curso(),
    }

    if aba_ativa == 'visao-geral':

        contexto['proximas_aulas'] = Aula.objects.filter(
            data__gte=hoje
        ).order_by('data', 'horario')[:5]

    if aba_ativa == 'frequencia':

        hoje, ano, mes, mes_anterior, proximo_mes = _parametros_calendario(request)
        semanas, _ = _semanas_do_calendario(ano, mes, hoje)
        presencas_por_aula = {
            presenca.aula_id: presenca.presente
            for presenca in Presenca.objects.filter(inscricao=inscricao)
        }

        for semana in semanas:

            for dia in semana:

                status_do_dia = ''

                for aula in dia['aulas']:

                    presenca = presencas_por_aula.get(aula.id)

                    if presenca is True:

                        aula.status_frequencia = 'presenca'

                        if status_do_dia != 'falta':

                            status_do_dia = 'presenca'

                    elif presenca is False:

                        aula.status_frequencia = 'falta'
                        status_do_dia = 'falta'

                    else:

                        aula.status_frequencia = 'neutro'

                dia['status_frequencia'] = status_do_dia

        contexto.update(
            {
                'semanas': semanas,
                'nome_mes': MESES[mes],
                'ano': ano,
                'mes_anterior': mes_anterior,
                'proximo_mes': proximo_mes,
            }
        )

    return render(
        request,
        'inscricoes/dashboard_aluna.html',
        contexto
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

    if not request.user.is_staff and _inscricao_aprovada_do_usuario(request.user):

        return redirect('dashboard_aluna')

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
                'status_choices': Inscricao.STATUS,
            }
        )

    return render(
        request,
        'inscricoes/listar_inscricoes.html',
        {'inscricoes': inscricoes}
    )


@login_required
@require_POST
def atualizar_status_inscricao(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    inscricao = get_object_or_404(Inscricao, id=id)
    status = request.POST.get('status')
    status_validos = {valor for valor, _ in Inscricao.STATUS}
    redirect_to = request.POST.get('next') or reverse('listar_inscricoes')

    if not url_has_allowed_host_and_scheme(
        redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):

        redirect_to = reverse('listar_inscricoes')

    if status not in status_validos:

        messages.warning(
            request,
            'Status de matricula invalido.'
        )

        return redirect(redirect_to)

    inscricao.status = status
    inscricao.save(update_fields=['status'])

    messages.success(
        request,
        'Status da matricula atualizado com sucesso.'
    )

    return redirect(redirect_to)


@login_required
@require_POST
def liberar_certificado(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    inscricao = get_object_or_404(Inscricao, id=id)
    redirect_to = request.POST.get('next') or reverse('detalhes_inscricao', args=[inscricao.id])

    if not url_has_allowed_host_and_scheme(
        redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):

        redirect_to = reverse('detalhes_inscricao', args=[inscricao.id])

    if not inscricao.certificado_conteudo:

        messages.warning(
            request,
            'Anexe o arquivo do certificado antes de liberar para a aluna.'
        )

        return redirect('listar_certificados')

    inscricao.certificado_liberado = True
    inscricao.certificado_liberado_em = timezone.now()
    inscricao.curso_concluido = True
    inscricao.save(update_fields=['certificado_liberado', 'certificado_liberado_em', 'curso_concluido'])

    messages.success(
        request,
        'Certificado liberado com sucesso.'
    )

    return redirect(redirect_to)


@login_required
@require_POST
def upload_certificado(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    inscricao = get_object_or_404(
        Inscricao,
        id=id,
        status='aprovada'
    )

    form = CertificadoUploadForm(
        request.POST,
        request.FILES
    )

    if form.is_valid():

        arquivo = form.cleaned_data['certificado_arquivo']
        inscricao.certificado_nome_arquivo = arquivo.name
        inscricao.certificado_tipo_arquivo = arquivo.content_type or ''
        inscricao.certificado_conteudo = arquivo.read()
        inscricao.certificado_liberado = True
        inscricao.certificado_liberado_em = timezone.now()
        inscricao.curso_concluido = True
        inscricao.save(
            update_fields=[
                'certificado_nome_arquivo',
                'certificado_tipo_arquivo',
                'certificado_conteudo',
                'certificado_liberado',
                'certificado_liberado_em',
                'curso_concluido',
            ]
        )

        messages.success(
            request,
            'Certificado anexado e liberado com sucesso.'
        )

    else:

        messages.warning(
            request,
            form.errors.get('certificado_arquivo', ['Nao foi possivel anexar o certificado.'])[0]
        )

    return redirect('listar_certificados')


@login_required
def baixar_certificado(request, id=None):

    if id is not None:

        inscricao = get_object_or_404(Inscricao, id=id)
        usuario_da_inscricao = inscricao.user_id == request.user.id
        email_da_inscricao = bool(request.user.email and inscricao.email == request.user.email)

        if not request.user.is_staff and not (usuario_da_inscricao or email_da_inscricao):

            return redirect('dashboard_aluna')

    else:

        inscricao = _inscricao_aprovada_do_usuario(request.user)

        if not inscricao:

            return redirect('listar_inscricoes')

    if not inscricao.certificado_disponivel:

        messages.warning(
            request,
            'O certificado ainda nao esta disponivel para download.'
        )

        if request.user.is_staff:

            return redirect('listar_certificados')

        return redirect('dashboard_aluna')

    filename = inscricao.certificado_nome_arquivo or 'certificado'
    content_type = inscricao.certificado_tipo_arquivo

    if not content_type:

        content_type, _ = mimetypes.guess_type(filename)

    response = HttpResponse(
        bytes(inscricao.certificado_conteudo),
        content_type=content_type or 'application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@login_required
@require_POST
def confirmar_exclusao_inscricoes(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    ids = request.POST.getlist('inscricoes_selecionadas')

    if not ids:

        messages.warning(
            request,
            'Selecione pelo menos uma inscricao para excluir.'
        )

        return redirect('listar_inscricoes')

    inscricoes = Inscricao.objects.filter(id__in=ids).order_by('-data_criacao')

    return render(
        request,
        'inscricoes/confirmar_exclusao_admin.html',
        {
            'tipo': 'inscricoes',
            'titulo': 'Excluir inscricoes',
            'descricao': 'Revise as inscricoes selecionadas antes de remover da plataforma.',
            'itens': inscricoes,
            'input_name': 'inscricoes_selecionadas',
            'action_url': 'excluir_inscricoes',
            'back_url': 'listar_inscricoes',
            'confirm_label': 'Sim, excluir inscricoes',
            'current_admin_page': 'inscricoes',
        }
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
    form_class = AdminInscricaoForm if request.user.is_staff else InscricaoForm

    if request.method == 'POST':

        form = form_class(
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

        form = form_class(instance=inscricao)

    return render(
        request,
        'inscricoes/editar_matricula.html',
        {
            'form': form,
            'inscricao': inscricao,
            'base_template': 'inscricoes/admin_base.html' if request.user.is_staff else 'inscricoes/base.html',
            'current_admin_page': 'inscricoes' if request.user.is_staff else None,
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
@require_POST
def confirmar_exclusao_aulas(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    ids = request.POST.getlist('aulas_selecionadas')

    if not ids:

        messages.warning(
            request,
            'Selecione pelo menos uma aula para excluir.'
        )

        return redirect('listar_aulas')

    aulas = Aula.objects.filter(id__in=ids).order_by('-data', '-horario')

    return render(
        request,
        'inscricoes/confirmar_exclusao_admin.html',
        {
            'tipo': 'aulas',
            'titulo': 'Excluir aulas',
            'descricao': 'Revise as aulas selecionadas antes de remover da plataforma.',
            'itens': aulas,
            'input_name': 'aulas_selecionadas',
            'action_url': 'excluir_aulas',
            'back_url': 'listar_aulas',
            'confirm_label': 'Sim, excluir aulas',
            'current_admin_page': 'aulas',
        }
    )


@login_required
@require_POST
def excluir_aulas(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    ids = request.POST.getlist('aulas_selecionadas')

    if not ids:

        messages.warning(
            request,
            'Selecione pelo menos uma aula para excluir.'
        )

        return redirect('listar_aulas')

    total_excluido, _ = Aula.objects.filter(id__in=ids).delete()

    messages.success(
        request,
        f'{total_excluido} aula(s) excluida(s) com sucesso.'
    )

    return redirect('listar_aulas')


@login_required
def calendario_aulas(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    hoje, ano, mes, mes_anterior, proximo_mes = _parametros_calendario(request)

    primeiro_dia = date(ano, mes, 1)
    _, ultimo_dia = calendar.monthrange(ano, mes)

    semanas, aulas = _semanas_do_calendario(ano, mes, hoje)

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


def vitrine(request):

    produtos = Produto.objects.filter(ativo=True)
    servicos = Servico.objects.filter(ativo=True)

    q = request.GET.get('q', '').strip()
    preco_max = request.GET.get('preco_max', '').strip()
    tipo = request.GET.get('tipo', '')

    if q:

        produtos = produtos.filter(
            Q(nome__icontains=q)
            | Q(descricao__icontains=q)
            | Q(categoria__icontains=q)
        )
        servicos = servicos.filter(
            Q(nome__icontains=q)
            | Q(descricao__icontains=q)
            | Q(tipo__icontains=q)
        )

    if preco_max:
        try:
            produtos = produtos.filter(preco__lte=float(preco_max))
        except ValueError:
            pass

    if tipo == 'produto':
        servicos = servicos.none()
    elif tipo == 'servico':
        produtos = produtos.none()

    sem_resultados = not produtos.exists() and not servicos.exists()
    total_produtos = produtos.count()
    total_servicos = servicos.count()
    total_itens = total_produtos + total_servicos
    itens_vitrine = [
        {
            'objeto': produto,
            'tipo': 'produto',
            'etiqueta': produto.categoria,
            'imagem_url': 'imagem_vitrine_produto',
            'mostrar_preco': True,
        }
        for produto in produtos
    ] + [
        {
            'objeto': servico,
            'tipo': 'servico',
            'etiqueta': servico.tipo,
            'imagem_url': 'imagem_vitrine_servico',
            'mostrar_preco': False,
        }
        for servico in servicos
    ]
    paginator = Paginator(itens_vitrine, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    querystring_sem_page = query_params.urlencode()

    if tipo == 'produto':
        contador = f'{total_produtos} produto' + ('' if total_produtos == 1 else 's')
    elif tipo == 'servico':
        contador = f'{total_servicos} serviço' + ('' if total_servicos == 1 else 's')
    else:
        contador = '1 item encontrado' if total_itens == 1 else f'{total_itens} itens encontrados'

    return render(
        request,
        'bazar/vitrine.html',
        {
            'produtos': produtos,
            'servicos': servicos,
            'itens_vitrine': page_obj.object_list,
            'page_obj': page_obj,
            'querystring_sem_page': querystring_sem_page,
            'sem_resultados': sem_resultados,
            'total_produtos': total_produtos,
            'total_servicos': total_servicos,
            'total_itens': total_itens,
            'contador': contador,
            'filtros': {
                'q': q,
                'preco_max': preco_max,
                'tipo': tipo,
            },
        }
    )


def imagem_vitrine_produto(request, id):

    produto = get_object_or_404(Produto, id=id, ativo=True)

    if not produto.tem_imagem:

        return HttpResponse(status=404)

    imagem = produto.imagem_capa

    if imagem:

        return HttpResponse(
            bytes(imagem.conteudo),
            content_type=imagem.tipo or 'application/octet-stream'
        )

    return HttpResponse(
        bytes(produto.imagem_conteudo),
        content_type=produto.imagem_tipo or 'application/octet-stream'
    )


def imagem_vitrine_servico(request, id):

    servico = get_object_or_404(Servico, id=id, ativo=True)

    if not servico.tem_imagem:

        return HttpResponse(status=404)

    imagem = servico.imagem_capa

    if imagem:

        return HttpResponse(
            bytes(imagem.conteudo),
            content_type=imagem.tipo or 'application/octet-stream'
        )

    return HttpResponse(
        bytes(servico.imagem_conteudo),
        content_type=servico.imagem_tipo or 'application/octet-stream'
    )
