from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from inscricoes.models import (
    Aula,
    Inscricao,
    Presenca,
    Produto,
    ProdutoImagem,
    Servico,
    SolicitacaoContato,
)


User = get_user_model()


def criar_usuario(email='aluna@example.com', senha='senha-teste-123', staff=False):

    return User.objects.create_user(
        username=email,
        email=email,
        password=senha,
        is_staff=staff,
        is_superuser=staff,
    )


def criar_inscricao(user=None, **kwargs):

    dados = {
        'nome': 'Maria Teste',
        'email': user.email if user else 'maria@example.com',
        'cpf': '52998224725',
        'data_nascimento': '2000-01-01',
        'telefone': '11900000000',
        'disponibilidade': 'manha',
        'status': 'pendente',
    }
    dados.update(kwargs)

    return Inscricao.objects.create(user=user, **dados)


def arquivo_imagem(nome='imagem.png'):

    return SimpleUploadedFile(
        nome,
        b'imagem-de-teste',
        content_type='image/png'
    )


class Epico1FormularioInscricaoTests(TestCase):

    def test_epico1_h1_inscricao_no_curso_com_sucesso(self):

        usuario = criar_usuario()
        self.client.force_login(usuario)

        response = self.client.post(
            reverse('criar_inscricao'),
            {
                'nome': 'Maria Teste',
                'cpf': '529.982.247-25',
                'data_nascimento': '2000-01-01',
                'telefone': '(11) 90000-0000',
                'disponibilidade': 'manha',
                'observacoes': 'Quero participar.',
            }
        )

        self.assertRedirects(response, reverse('sucesso'))
        self.assertTrue(
            Inscricao.objects.filter(
                user=usuario,
                email=usuario.email,
                cpf='52998224725'
            ).exists()
        )

    def test_epico1_h1_inscricao_com_campos_obrigatorios_invalidos(self):

        usuario = criar_usuario()
        self.client.force_login(usuario)

        response = self.client.post(reverse('criar_inscricao'), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inscricao.objects.count(), 0)
        self.assertContains(response, 'Informe o nome completo.')

    def test_epico1_h1_inscricao_com_cpf_ou_telefone_invalidos(self):

        usuario = criar_usuario()
        self.client.force_login(usuario)

        response = self.client.post(
            reverse('criar_inscricao'),
            {
                'nome': 'Maria Teste',
                'cpf': 'abc',
                'data_nascimento': '2000-01-01',
                'telefone': 'telefone',
                'disponibilidade': 'manha',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inscricao.objects.count(), 0)
        self.assertContains(response, 'Informe um CPF')

    def test_epico1_h2_admin_visualiza_inscricoes_registradas(self):

        admin = criar_usuario('admin@example.com', staff=True)
        criar_inscricao(nome='Ana Lista', email='ana@example.com')
        self.client.force_login(admin)

        response = self.client.get(reverse('listar_inscricoes'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Lista')
        self.assertContains(response, '529.982.247-25')
        self.assertContains(response, 'Costurando Sonhos')

    def test_epico1_h2_admin_visualiza_lista_sem_inscricoes(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)

        response = self.client.get(reverse('listar_inscricoes'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mostrando 0-0 de 0')

    def test_epico1_h2_admin_visualiza_detalhes_da_inscricao(self):

        admin = criar_usuario('admin@example.com', staff=True)
        inscricao = criar_inscricao(nome='Ana Detalhe', email='detalhe@example.com')
        self.client.force_login(admin)

        response = self.client.get(reverse('detalhes_inscricao', args=[inscricao.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Detalhe')
        self.assertContains(response, 'detalhe@example.com')

    def test_epico1_h3_aluna_atualiza_matricula(self):

        usuario = criar_usuario()
        inscricao = criar_inscricao(user=usuario)
        self.client.force_login(usuario)

        response = self.client.post(
            reverse('editar_matricula', args=[inscricao.id]),
            {
                'nome': 'Maria Atualizada',
                'cpf': '529.982.247-25',
                'data_nascimento': '2000-01-01',
                'telefone': '(11) 98888-7777',
                'disponibilidade': 'tarde',
                'observacoes': 'Atualizado.',
            }
        )

        self.assertRedirects(response, reverse('listar_inscricoes'))
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.nome, 'Maria Atualizada')
        self.assertEqual(inscricao.telefone, '11988887777')

    def test_epico1_h3_aluna_cancela_matricula(self):

        usuario = criar_usuario()
        inscricao = criar_inscricao(user=usuario)
        self.client.force_login(usuario)

        response = self.client.post(reverse('cancelar_matricula', args=[inscricao.id]))

        self.assertRedirects(response, reverse('listar_inscricoes'))
        self.assertFalse(Inscricao.objects.filter(id=inscricao.id).exists())

    def test_epico1_h3_edicao_com_dados_invalidos_nao_atualiza(self):

        usuario = criar_usuario()
        inscricao = criar_inscricao(user=usuario)
        self.client.force_login(usuario)

        response = self.client.post(
            reverse('editar_matricula', args=[inscricao.id]),
            {
                'nome': '',
                'cpf': 'abc',
                'data_nascimento': '2035-01-01',
                'telefone': 'abc',
                'disponibilidade': '',
            }
        )

        self.assertEqual(response.status_code, 200)
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.nome, 'Maria Teste')


class Epico2AcompanhamentoTests(TestCase):

    def test_epico2_h1_instrutor_registra_presenca(self):

        admin = criar_usuario('admin@example.com', staff=True)
        aluna = criar_usuario('aluna@example.com')
        inscricao = criar_inscricao(user=aluna, status='aprovada')
        aula = Aula.objects.create(
            data=timezone.localdate() + timedelta(days=1),
            horario='09:00',
            topico='Aula de teste'
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse('registrar_presenca', args=[aula.id]),
            {f'presente_{inscricao.id}': 'on'}
        )

        self.assertRedirects(response, reverse('registrar_presenca', args=[aula.id]))
        self.assertTrue(
            Presenca.objects.get(aula=aula, inscricao=inscricao).presente
        )

    def test_epico2_h1_presenca_registrada_aparece_ao_reabrir_aula(self):

        admin = criar_usuario('admin@example.com', staff=True)
        aluna = criar_usuario('aluna@example.com')
        inscricao = criar_inscricao(user=aluna, status='aprovada')
        aula = Aula.objects.create(
            data=timezone.localdate() + timedelta(days=1),
            horario='09:00',
            topico='Aula de teste'
        )
        Presenca.objects.create(aula=aula, inscricao=inscricao, presente=True)
        self.client.force_login(admin)

        response = self.client.get(reverse('registrar_presenca', args=[aula.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, inscricao.nome)

    def test_epico2_h2_admin_cadastra_aula_e_visualiza_calendario(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)
        data_aula = timezone.localdate() + timedelta(days=7)

        response = self.client.post(
            reverse('criar_aula'),
            {
                'data': data_aula.isoformat(),
                'horario': '10:30',
                'topico': 'Modelagem'
            }
        )

        self.assertRedirects(response, reverse('listar_aulas'))
        calendario = self.client.get(
            reverse('calendario_aulas'),
            {'ano': data_aula.year, 'mes': data_aula.month}
        )
        self.assertContains(calendario, 'Modelagem')

    def test_epico2_h2_admin_atualiza_aula(self):

        admin = criar_usuario('admin@example.com', staff=True)
        aula = Aula.objects.create(
            data=timezone.localdate() + timedelta(days=7),
            horario='10:00',
            topico='Antigo'
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse('editar_aula', args=[aula.id]),
            {
                'data': aula.data.isoformat(),
                'horario': '11:00',
                'topico': 'Novo'
            }
        )

        self.assertRedirects(response, reverse('listar_aulas'))
        aula.refresh_from_db()
        self.assertEqual(aula.topico, 'Novo')

    def test_epico2_h2_admin_nao_cadastra_aula_com_data_passada(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('criar_aula'),
            {
                'data': (timezone.localdate() - timedelta(days=1)).isoformat(),
                'horario': '10:30',
                'topico': 'Invalida'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Aula.objects.exists())

    def test_epico2_h3_admin_libera_certificado_para_aluna_concluida(self):

        admin = criar_usuario('admin@example.com', staff=True)
        aluna = criar_usuario('aluna@example.com')
        inscricao = criar_inscricao(user=aluna, status='aprovada', curso_concluido=True)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('upload_certificado', args=[inscricao.id]),
            {
                'certificado_arquivo': SimpleUploadedFile(
                    'certificado.pdf',
                    b'%PDF-1.4 teste',
                    content_type='application/pdf'
                )
            }
        )

        self.assertRedirects(response, reverse('listar_certificados'))
        inscricao.refresh_from_db()
        self.assertTrue(inscricao.certificado_disponivel)

    def test_epico2_h3_certificado_nao_disponivel_sem_liberacao(self):

        aluna = criar_usuario('aluna@example.com')
        criar_inscricao(user=aluna, status='aprovada')
        self.client.force_login(aluna)

        response = self.client.get(reverse('baixar_certificado'))

        self.assertRedirects(response, reverse('dashboard_aluna'))

    def test_epico2_h4_usuario_aprovado_acessa_area_da_aluna(self):

        aluna = criar_usuario('aluna@example.com')
        criar_inscricao(user=aluna, status='aprovada')
        self.client.force_login(aluna)

        response = self.client.get(reverse('dashboard_aluna'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Teste')

    def test_epico2_h4_usuario_nao_logado_acessa_bazar(self):

        response = self.client.get(reverse('vitrine'))

        self.assertEqual(response.status_code, 200)

    def test_epico2_h4_mudanca_de_status_atualiza_area_principal(self):

        admin = criar_usuario('admin@example.com', staff=True)
        aluna = criar_usuario('aluna@example.com')
        inscricao = criar_inscricao(user=aluna, status='pendente')
        self.client.force_login(admin)

        self.client.post(
            reverse('atualizar_status_inscricao', args=[inscricao.id]),
            {'status': 'aprovada', 'next': reverse('listar_inscricoes')}
        )
        inscricao.refresh_from_db()

        self.assertEqual(inscricao.status, 'aprovada')


class Epico3BazarTests(TestCase):

    def test_epico3_h1_admin_cadastra_produto(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('criar_produto'),
            {
                'nome': 'Bolsa Artesanal',
                'descricao': 'Bolsa feita pelas alunas.',
                'preco': '79.90',
                'categoria': 'Bolsas',
                'ativo': 'on',
                'imagem': arquivo_imagem(),
            }
        )

        self.assertRedirects(response, reverse('listar_produtos'))
        self.assertTrue(Produto.objects.filter(nome='Bolsa Artesanal').exists())

    def test_epico3_h1_admin_cadastra_servico(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('criar_servico'),
            {
                'nome': 'Ajuste de roupa',
                'descricao': 'Servico de ajuste sob consulta.',
                'tipo': 'Costura',
                'ativo': 'on',
                'imagem': arquivo_imagem(),
            }
        )

        self.assertRedirects(response, reverse('listar_servicos'))
        self.assertTrue(Servico.objects.filter(nome='Ajuste de roupa').exists())

    def test_epico3_h1_cadastro_invalido_nao_cria_produto(self):

        admin = criar_usuario('admin@example.com', staff=True)
        self.client.force_login(admin)

        response = self.client.post(
            reverse('criar_produto'),
            {
                'nome': '',
                'descricao': '',
                'preco': '-1',
                'categoria': '',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Produto.objects.exists())

    def test_epico3_h2_vitrine_exibe_produtos_e_servicos(self):

        Produto.objects.create(
            nome='Bolsa Floral',
            descricao='Produto artesanal.',
            preco='39.90',
            categoria='Bolsas',
            ativo=True
        )
        Servico.objects.create(
            nome='Ajuste simples',
            descricao='Servico artesanal.',
            tipo='Costura',
            ativo=True
        )

        response = self.client.get(reverse('vitrine'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bolsa Floral')
        self.assertContains(response, 'Ajuste simples')

    def test_epico3_h2_vitrine_filtra_por_produto(self):

        Produto.objects.create(
            nome='Bolsa Azul',
            descricao='Produto artesanal.',
            preco='39.90',
            categoria='Bolsas',
            ativo=True
        )
        Servico.objects.create(
            nome='Ajuste invisivel',
            descricao='Servico artesanal.',
            tipo='Costura',
            ativo=True
        )

        response = self.client.get(reverse('vitrine'), {'q': 'Bolsa'})

        self.assertContains(response, 'Bolsa Azul')
        self.assertNotContains(response, 'Ajuste invisivel')

    def test_epico3_h2_vitrine_mostra_estado_sem_resultado(self):

        response = self.client.get(reverse('vitrine'), {'q': 'nada-encontrado'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nenhum item encontrado')

    def test_epico3_h3_admin_visualiza_contatos_recebidos_no_django_admin(self):

        admin = criar_usuario('admin@example.com', staff=True)
        SolicitacaoContato.objects.create(
            tipo='doacao',
            nome='Pessoa Doadora',
            email='doadora@example.com',
            telefone='11900000000',
            mensagem='Quero doar.'
        )
        self.client.force_login(admin)

        response = self.client.get('/django-admin/inscricoes/solicitacaocontato/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pessoa Doadora')

    def test_epico3_h3_admin_visualiza_detalhe_do_formulario(self):

        admin = criar_usuario('admin@example.com', staff=True)
        solicitacao = SolicitacaoContato.objects.create(
            tipo='parceria',
            nome='Parceira',
            email='parceira@example.com',
            telefone='11900000000',
            mensagem='Quero propor parceria.'
        )
        self.client.force_login(admin)

        response = self.client.get(
            f'/django-admin/inscricoes/solicitacaocontato/{solicitacao.id}/change/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quero propor parceria.')

    def test_epico3_h3_admin_gerencia_status_da_solicitacao(self):

        solicitacao = SolicitacaoContato.objects.create(
            tipo='doacao',
            nome='Contato',
            email='contato@example.com',
            telefone='11900000000',
            mensagem='Mensagem.'
        )
        solicitacao.status = 'em_analise'
        solicitacao.save(update_fields=['status'])

        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, 'em_analise')

    def test_epico3_h4_envio_de_solicitacao_com_sucesso(self):

        response = self.client.post(
            reverse('contato'),
            {
                'tipo': 'parceria',
                'nome': 'Maria Teste',
                'email': 'maria@example.com',
                'telefone': '(11) 90000-0000',
                'mensagem': 'Quero propor uma parceria.',
            }
        )

        self.assertRedirects(response, reverse('contato'))
        self.assertTrue(SolicitacaoContato.objects.filter(email='maria@example.com').exists())

    def test_epico3_h4_solicitacao_de_doacao(self):

        response = self.client.post(
            reverse('contato'),
            {
                'tipo': 'doacao',
                'nome': 'Doadora',
                'email': 'doadora@example.com',
                'telefone': '11900000000',
                'mensagem': 'Quero fazer uma doacao.',
            }
        )

        self.assertRedirects(response, reverse('contato'))
        self.assertEqual(
            SolicitacaoContato.objects.get(email='doadora@example.com').tipo,
            'doacao'
        )

    def test_epico3_h4_solicitacao_de_parceria(self):

        self.client.post(
            reverse('contato'),
            {
                'tipo': 'parceria',
                'nome': 'Parceira',
                'email': 'parceira@example.com',
                'telefone': '11900000000',
                'mensagem': 'Quero propor uma parceria.',
            }
        )

        self.assertEqual(
            SolicitacaoContato.objects.get(email='parceira@example.com').tipo,
            'parceria'
        )

    def test_epico3_h4_dados_invalidos_nao_criam_solicitacao(self):

        response = self.client.post(
            reverse('contato'),
            {
                'tipo': 'parceria',
                'nome': '',
                'email': 'email-invalido',
                'telefone': '123',
                'mensagem': '',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SolicitacaoContato.objects.count(), 0)
