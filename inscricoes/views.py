import calendar
import json
import logging
import mimetypes
from datetime import date, timedelta
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
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
    SolicitacaoContatoForm,
    SuporteContatoForm,
    normalizar_cpf,
)
from .models import (
    Aula,
    Inscricao,
    Presenca,
    Produto,
    ProdutoImagem,
    Servico,
    ServicoImagem,
    SolicitacaoContato,
)


logger = logging.getLogger(__name__)

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


def _whatsapp_interesse_url(request, item, tipo_item, mostra_preco):

    whatsapp_contato = getattr(item, 'whatsapp_contato', '') or settings.WHATSAPP_CONTATO

    if not whatsapp_contato:

        return ''

    tipo_label = 'produto' if tipo_item == 'produto' else 'servico'
    valor_label = item.preco_formatado if mostra_preco else 'valor sob consulta'
    item_url = request.build_absolute_uri()
    mensagem = (
        f'Ola, tenho interesse no {tipo_label} "{item.nome}" '
        f'({valor_label}) que vi no bazar EntreLinhas. '
        f'Pode me passar mais informacoes? {item_url}'
    )

    return f'https://wa.me/{whatsapp_contato}?text={quote(mensagem)}'


def home(request):

    return render(
        request,
        'inscricoes/home.html'
    )


def _formatar_aula_lia(aula):

    topico = f' - {aula.topico}' if aula.topico else ''

    return f'{aula.data:%d/%m/%Y} as {aula.horario:%H:%M}{topico}'


def _contexto_aluna_lia(user):

    if not user.is_authenticated:

        return 'Nenhuma aluna logada foi identificada.'

    inscricao = _inscricao_aprovada_do_usuario(user)

    if not inscricao:

        return (
            'A pessoa esta logada, mas nao ha matricula aprovada vinculada. '
            'Oriente a verificar inscricoes ou falar com a equipe.'
        )

    total_aulas_registradas = Aula.objects.filter(
        data__lte=timezone.localdate()
    ).count()
    presencas_confirmadas = Presenca.objects.filter(
        inscricao=inscricao,
        aula__data__lte=timezone.localdate(),
        presente=True
    ).count()
    frequencia = inscricao.frequencia_percentual
    hoje = timezone.localdate()
    proximas_aulas = Aula.objects.filter(
        data__gte=hoje
    ).order_by('data', 'horario')[:3]

    if proximas_aulas:

        aulas_texto = '; '.join(_formatar_aula_lia(aula) for aula in proximas_aulas)

    else:

        aulas_texto = 'Nenhuma aula futura cadastrada no momento.'

    certificado_status = 'liberado para download' if inscricao.certificado_disponivel else 'ainda nao liberado'
    curso_concluido_lia = inscricao.certificado_disponivel

    return '\n'.join([
        'Contexto real da aluna logada:',
        f'- Nome: {inscricao.nome}',
        f'- Status da matricula: {inscricao.get_status_display()}',
        f'- Matricula ativa: {"sim" if inscricao.ativa else "nao"}',
        '- Curso: Costurando Sonhos.',
        f'- Disponibilidade informada: {inscricao.get_disponibilidade_display()}',
        f'- Frequencia: {presencas_confirmadas} presencas em {total_aulas_registradas} aulas registradas ({frequencia}%).',
        f'- Proximas aulas cadastradas: {aulas_texto}',
        f'- Curso concluido: {"sim" if curso_concluido_lia else "nao"}',
        f'- Certificado: {certificado_status}.',
    ])


def _resumo_item_lia(item, tipo):

    nome = item.nome
    categoria = getattr(item, 'categoria', '') or getattr(item, 'tipo', '')
    preco = getattr(item, 'preco_formatado', None)

    if preco:

        return f'{nome} ({categoria}, {preco})'

    return f'{nome} ({tipo}: {categoria})'


def _contexto_publico_lia():

    produtos = Produto.objects.filter(ativo=True).order_by('-data_criacao')
    servicos = Servico.objects.filter(ativo=True).order_by('-data_criacao')
    produtos_lista = list(produtos[:5])
    servicos_lista = list(servicos[:5])
    pix_configurado = bool(settings.PIX_CHAVE_ONG)
    whatsapp_configurado = bool(settings.WHATSAPP_CONTATO)

    return '\n'.join([
        'Contexto publico real da plataforma:',
        f'- Produtos ativos no bazar: {produtos.count()}.',
        f'- Exemplos de produtos ativos: {", ".join(_resumo_item_lia(produto, "produto") for produto in produtos_lista) if produtos_lista else "nenhum produto ativo no momento"}.',
        f'- Servicos ativos no bazar: {servicos.count()}.',
        f'- Exemplos de servicos ativos: {", ".join(_resumo_item_lia(servico, "servico") for servico in servicos_lista) if servicos_lista else "nenhum servico ativo no momento"}.',
        '- Formas de apoio: doacao via PIX quando configurado, parceria pela pagina Apoiar e interesse por itens do bazar via WhatsApp quando configurado.',
        '- Suporte da plataforma: use o formulario de suporte do chat; nao confunda suporte com doacao ou parceria.',
        f'- Chave PIX para doacoes: {settings.PIX_CHAVE_ONG if pix_configurado else "PIX ainda nao configurado"}.',
        f'- WhatsApp de contato geral: {"disponivel" if whatsapp_configurado else "nao configurado"}.',
    ])


def _prompt_lia(contexto, request=None):

    instrucoes = [
        'Voce e Lia, assistente virtual da ONG EntreLinhas.',
        'Responda em portugues do Brasil, com tom acolhedor, simples e objetivo.',
        'Ajude com inscricoes, cursos gratuitos, area da aluna, frequencia, certificados, bazar solidario, doacoes e parcerias.',
        'Nao invente datas, precos, vagas ou regras. Quando nao souber ou a pessoa precisar de atendimento humano, oriente a abrir o formulario de suporte disponivel no chat.',
        'Quando encaminhar para suporte humano, use a frase exata "abra o formulario de suporte" para que o chat mostre o botao correto.',
        'Nao solicite dados sensiveis como CPF completo, senha ou dados bancarios.',
        'A EntreLinhas oferece cursos profissionalizantes gratuitos e usa o bazar solidario para apoiar a ONG.',
        'A inscricao pode ser feita pelo site; alunas aprovadas acessam a area da aluna para acompanhar aulas, frequencia e certificados.',
    ]

    if contexto == 'student':

        instrucoes.extend([
            'A conversa acontece na area da aluna.',
            'Explique como a aluna pode consultar informacoes dentro da plataforma, sem pedir dados pessoais.',
            'Para alteracao de dados, oriente a procurar a opcao de matricula/dados cadastrais ou contato com a equipe quando necessario.',
        ])

        if request:

            instrucoes.append(_contexto_aluna_lia(request.user))

    else:

        instrucoes.extend([
            'A conversa acontece no site publico.',
            'Para visitantes, ajude com inscricao, gratuidade, cursos, bazar, doacao e parceria.',
        ])

        instrucoes.append(_contexto_publico_lia())

    return '\n'.join(instrucoes)


def _mensagens_lia(payload_mensagens):

    mensagens = []

    if not isinstance(payload_mensagens, list):

        return mensagens

    for mensagem in payload_mensagens[-12:]:

        if not isinstance(mensagem, dict):

            continue

        papel = mensagem.get('role')
        conteudo = mensagem.get('content')

        if papel not in {'user', 'assistant'} or not isinstance(conteudo, str):

            continue

        conteudo = conteudo.strip()

        if conteudo:

            mensagens.append({
                'role': papel,
                'content': conteudo[:1200],
            })

    return mensagens


def _resposta_groq(mensagens):

    payload = {
        'model': settings.GROQ_MODEL,
        'messages': mensagens,
        'temperature': 0.5,
        'max_tokens': 500,
    }

    requisicao = Request(
        settings.GROQ_API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {settings.GROQ_API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'EntreLinhas/1.0',
        },
        method='POST',
    )

    with urlopen(requisicao, timeout=30) as resposta:

        dados = json.loads(resposta.read().decode('utf-8'))

    return dados['choices'][0]['message']['content'].strip()


@require_POST
def chat_suporte(request):

    try:

        payload = json.loads(request.body.decode('utf-8') or '{}')

    except json.JSONDecodeError:

        return JsonResponse(
            {'error': 'Nao consegui ler sua mensagem. Tente enviar novamente.'},
            status=400
        )

    contexto = payload.get('context')

    if contexto not in {'public', 'student'}:

        contexto = 'public'

    mensagens_chat = _mensagens_lia(payload.get('messages'))

    if not mensagens_chat or mensagens_chat[-1]['role'] != 'user':

        return JsonResponse(
            {'error': 'Envie uma mensagem para a Lia responder.'},
            status=400
        )

    if not settings.GROQ_API_KEY:

        return JsonResponse(
            {
                'error': (
                    'Lia ainda nao esta configurada. '
                    'Tente novamente mais tarde ou abra o formulario de suporte.'
                )
            },
            status=503
        )

    mensagens_groq = [
        {
            'role': 'system',
            'content': _prompt_lia(contexto, request),
        },
        *mensagens_chat,
    ]

    try:

        resposta = _resposta_groq(mensagens_groq)

    except HTTPError as erro:

        corpo = erro.read().decode('utf-8', errors='ignore')[:500]
        logger.warning('Erro HTTP na Groq: status=%s body=%s', erro.code, corpo)
        payload_erro = {
            'error': (
                'A Lia nao conseguiu responder agora. '
                'Tente novamente em alguns instantes.'
            )
        }

        if settings.DEBUG:

            payload_erro['debug'] = f'Groq HTTP {erro.code}: {corpo}'

        return JsonResponse(payload_erro, status=502)

    except (URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as erro:

        logger.warning('Erro ao chamar Groq: %s', erro)
        payload_erro = {
            'error': (
                'A Lia nao conseguiu responder agora. '
                'Tente novamente em alguns instantes.'
            )
        }

        if settings.DEBUG:

            payload_erro['debug'] = str(erro)

        return JsonResponse(
            payload_erro,
            status=502
        )

    return JsonResponse({'reply': resposta})


def contato(request):

    tipo_inicial = request.GET.get('tipo')

    if tipo_inicial not in {'doacao', 'parceria'}:

        tipo_inicial = 'doacao'

    if request.method == 'POST':

        form = SolicitacaoContatoForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(
                request,
                'Solicitacao enviada com sucesso. Nossa equipe entrara em contato.'
            )

            return redirect('contato')

        messages.warning(
            request,
            'Nao foi possivel enviar sua solicitacao. Revise os campos destacados.'
        )

    else:

        form = SolicitacaoContatoForm(initial={'tipo': tipo_inicial})

    return render(
        request,
        'inscricoes/contato.html',
        {
            'form': form,
            'tipo_inicial': tipo_inicial,
            'pix_chave_ong': settings.PIX_CHAVE_ONG,
        }
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


def suporte(request):

    initial = {}

    if request.user.is_authenticated:

        initial['email'] = request.user.email

        inscricao = _inscricao_aprovada_do_usuario(request.user)

        if inscricao:

            initial['nome'] = inscricao.nome
            initial['telefone'] = inscricao.telefone

        elif request.user.get_full_name():

            initial['nome'] = request.user.get_full_name()

    if request.method == 'POST':

        form = SuporteContatoForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(
                request,
                'Mensagem enviada ao suporte. Nossa equipe entrara em contato.'
            )

            return redirect('suporte')

        messages.warning(
            request,
            'Nao foi possivel enviar sua mensagem. Revise os campos destacados.'
        )

    else:

        form = SuporteContatoForm(initial=initial)

    return render(
        request,
        'inscricoes/suporte.html',
        {
            'form': form,
        }
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

    hoje = timezone.localdate()
    inicio_mes_atual = hoje.replace(day=1)

    if inicio_mes_atual.month == 1:

        inicio_mes_anterior = inicio_mes_atual.replace(
            year=inicio_mes_atual.year - 1,
            month=12
        )

    else:

        inicio_mes_anterior = inicio_mes_atual.replace(
            month=inicio_mes_atual.month - 1
        )

    total_inscricoes = Inscricao.objects.count()
    inscricoes_mes_atual = Inscricao.objects.filter(
        data_criacao__date__gte=inicio_mes_atual
    ).count()
    inscricoes_mes_anterior = Inscricao.objects.filter(
        data_criacao__date__gte=inicio_mes_anterior,
        data_criacao__date__lt=inicio_mes_atual
    ).count()
    alunas_ativas = Inscricao.objects.filter(
        ativa=True,
        status='aprovada'
    ).count()
    produtos_ativos = Produto.objects.filter(ativo=True).count()
    servicos_ativos = Servico.objects.filter(ativo=True).count()
    itens_bazar = produtos_ativos + servicos_ativos
    itens_bazar_semana = (
        Produto.objects.filter(
            ativo=True,
            data_criacao__date__gte=hoje - timedelta(days=7)
        ).count()
        + Servico.objects.filter(
            ativo=True,
            data_criacao__date__gte=hoje - timedelta(days=7)
        ).count()
    )
    solicitacoes_novas = SolicitacaoContato.objects.filter(
        status='nova'
    ).count()
    proximas_aulas = Aula.objects.filter(
        data__gte=hoje
    ).order_by('data', 'horario')[:3]
    solicitacoes_recentes = SolicitacaoContato.objects.select_related().order_by(
        '-criada_em'
    )[:3]

    if inscricoes_mes_anterior:

        variacao_inscricoes = round(
            (
                (inscricoes_mes_atual - inscricoes_mes_anterior)
                / inscricoes_mes_anterior
            ) * 100
        )
        inscricoes_auxiliar = f'{variacao_inscricoes:+d}% vs. mes passado'
        inscricoes_auxiliar_estado = 'positive' if variacao_inscricoes >= 0 else 'neutral'

    else:

        inscricoes_auxiliar = 'Sem base no mes passado'
        inscricoes_auxiliar_estado = 'neutral'

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
            'inscricoes_mes_atual': inscricoes_mes_atual,
            'inscricoes_auxiliar': inscricoes_auxiliar,
            'inscricoes_auxiliar_estado': inscricoes_auxiliar_estado,
            'alunas_ativas': alunas_ativas,
            'produtos_ativos': produtos_ativos,
            'servicos_ativos': servicos_ativos,
            'itens_bazar': itens_bazar,
            'itens_bazar_semana': itens_bazar_semana,
            'solicitacoes_novas': solicitacoes_novas,
            'proximas_aulas': proximas_aulas,
            'solicitacoes_recentes': solicitacoes_recentes,
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
            'imagens': produto.imagens.all(),
            'imagem_galeria_url': 'imagem_vitrine_produto_galeria',
            'excluir_imagem_url': 'excluir_imagem_produto',
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
@require_POST
def excluir_imagem_produto(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    imagem = get_object_or_404(ProdutoImagem, id=id)
    produto_id = imagem.produto_id
    imagem.delete()
    messages.success(request, 'Imagem excluida com sucesso.')

    return redirect('editar_produto', id=produto_id)


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
            'imagens': servico.imagens.all(),
            'imagem_galeria_url': 'imagem_vitrine_servico_galeria',
            'excluir_imagem_url': 'excluir_imagem_servico',
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
def listar_solicitacoes(request):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()
    solicitacoes = SolicitacaoContato.objects.filter(
        tipo='suporte'
    ).order_by('-criada_em')

    status_validos = {opcao[0] for opcao in SolicitacaoContato.STATUS}

    if status in status_validos:

        solicitacoes = solicitacoes.filter(status=status)

    else:

        status = ''

    if q:

        solicitacoes = solicitacoes.filter(
            Q(nome__icontains=q)
            | Q(email__icontains=q)
            | Q(telefone__icontains=q)
            | Q(mensagem__icontains=q)
        )

    paginator = Paginator(solicitacoes, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'inscricoes/listar_solicitacoes.html',
        {
            'current_admin_page': 'solicitacoes',
            'solicitacoes': page_obj.object_list,
            'page_obj': page_obj,
            'total_count': paginator.count,
            'start_index': page_obj.start_index() if paginator.count else 0,
            'end_index': page_obj.end_index() if paginator.count else 0,
            'status_selecionado': status,
            'q': q,
            'status_opcoes': SolicitacaoContato.STATUS,
        }
    )


@login_required
@require_POST
def atualizar_status_solicitacao(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    solicitacao = get_object_or_404(
        SolicitacaoContato,
        id=id,
        tipo='suporte'
    )
    novo_status = request.POST.get('status', '')
    status_validos = {opcao[0] for opcao in SolicitacaoContato.STATUS}

    if novo_status in status_validos:

        solicitacao.status = novo_status
        solicitacao.save(update_fields=['status', 'atualizada_em'])
        messages.success(request, 'Status da solicitacao atualizado com sucesso.')

    else:

        messages.warning(request, 'Escolha um status valido para a solicitacao.')

    proxima_url = request.POST.get('next') or reverse('listar_solicitacoes')

    if not url_has_allowed_host_and_scheme(
        proxima_url,
        allowed_hosts={request.get_host()}
    ):

        proxima_url = reverse('listar_solicitacoes')

    return redirect(proxima_url)


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
    aulas_passadas = Aula.objects.filter(data__lte=hoje)
    presencas = Presenca.objects.filter(
        inscricao=inscricao,
        aula__data__lte=hoje
    )
    aulas_registradas = aulas_passadas.count()
    presencas_confirmadas = presencas.filter(presente=True).count()
    faltas = max(aulas_registradas - presencas_confirmadas, 0)
    frequencia = round((presencas_confirmadas / aulas_registradas) * 100) if aulas_registradas else 0

    contexto = {
        'inscricao': inscricao,
        'aba_ativa': aba_ativa,
        'aulas_registradas': aulas_registradas,
        'presencas_confirmadas': presencas_confirmadas,
        'faltas': faltas,
        'frequencia': frequencia,
        'curso_concluido': inscricao.certificado_disponivel,
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

                    elif presenca is False or aula.data <= hoje:

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


def imagem_vitrine_produto_galeria(request, id):

    imagem = get_object_or_404(
        ProdutoImagem,
        id=id,
        produto__ativo=True
    )

    return HttpResponse(
        bytes(imagem.conteudo),
        content_type=imagem.tipo or 'application/octet-stream'
    )


def detalhe_vitrine_produto(request, id):

    produto = get_object_or_404(Produto, id=id, ativo=True)
    imagens = list(produto.imagens.all())

    return render(
        request,
        'bazar/detalhe.html',
        {
            'item': produto,
            'tipo_item': 'produto',
            'etiqueta': produto.categoria,
            'imagens': imagens,
            'imagem_capa_url': 'imagem_vitrine_produto',
            'imagem_galeria_url': 'imagem_vitrine_produto_galeria',
            'mostra_preco': True,
            'whatsapp_url': _whatsapp_interesse_url(
                request,
                produto,
                'produto',
                True
            ),
            'whatsapp_disponivel': bool(produto.whatsapp_contato or settings.WHATSAPP_CONTATO),
        }
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


@login_required
@require_POST
def excluir_imagem_servico(request, id):

    if not request.user.is_staff:

        return redirect('listar_inscricoes')

    imagem = get_object_or_404(ServicoImagem, id=id)
    servico_id = imagem.servico_id
    imagem.delete()
    messages.success(request, 'Imagem excluida com sucesso.')

    return redirect('editar_servico', id=servico_id)


def imagem_vitrine_servico_galeria(request, id):

    imagem = get_object_or_404(
        ServicoImagem,
        id=id,
        servico__ativo=True
    )

    return HttpResponse(
        bytes(imagem.conteudo),
        content_type=imagem.tipo or 'application/octet-stream'
    )


def detalhe_vitrine_servico(request, id):

    servico = get_object_or_404(Servico, id=id, ativo=True)
    imagens = list(servico.imagens.all())

    return render(
        request,
        'bazar/detalhe.html',
        {
            'item': servico,
            'tipo_item': 'servico',
            'etiqueta': servico.tipo,
            'imagens': imagens,
            'imagem_capa_url': 'imagem_vitrine_servico',
            'imagem_galeria_url': 'imagem_vitrine_servico_galeria',
            'mostra_preco': False,
            'whatsapp_url': _whatsapp_interesse_url(
                request,
                servico,
                'servico',
                False
            ),
            'whatsapp_disponivel': bool(settings.WHATSAPP_CONTATO),
        }
    )
