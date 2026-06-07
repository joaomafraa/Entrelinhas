from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
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


class Command(BaseCommand):
    help = 'Prepara dados previsiveis para os testes Cypress.'

    def handle(self, *args, **options):

        User = get_user_model()
        emails = [
            'cypress-admin@example.com',
            'cypress-aluna@example.com',
            'cypress-edicao@example.com',
            'cypress-nova@example.com',
        ]

        User.objects.filter(email__in=emails).delete()
        Inscricao.objects.filter(email__in=emails).delete()
        SolicitacaoContato.objects.filter(email__icontains='cypress').delete()
        Produto.objects.filter(nome__icontains='Cypress').delete()
        Servico.objects.filter(nome__icontains='Cypress').delete()
        Aula.objects.filter(topico__icontains='Cypress').delete()

        admin = User.objects.create_superuser(
            username='cypress-admin@example.com',
            email='cypress-admin@example.com',
            password='cypress12345',
            first_name='Admin',
            last_name='Cypress',
        )
        aluna = User.objects.create_user(
            username='cypress-aluna@example.com',
            email='cypress-aluna@example.com',
            password='cypress12345',
            first_name='Aluna',
            last_name='Cypress',
        )
        aluna_edicao = User.objects.create_user(
            username='cypress-edicao@example.com',
            email='cypress-edicao@example.com',
            password='cypress12345',
            first_name='Edicao',
            last_name='Cypress',
        )

        inscricao = Inscricao.objects.create(
            user=aluna,
            nome='Aluna Cypress',
            email='cypress-aluna@example.com',
            cpf='52998224725',
            data_nascimento='2000-01-01',
            telefone='11900000000',
            disponibilidade='manha',
            status='aprovada',
            curso_concluido=True,
            certificado_liberado=True,
            certificado_liberado_em=timezone.now(),
            certificado_nome_arquivo='certificado-cypress.pdf',
            certificado_tipo_arquivo='application/pdf',
            certificado_conteudo=b'%PDF-1.4 cypress',
        )
        Inscricao.objects.create(
            user=aluna_edicao,
            nome='Edicao Cypress',
            email='cypress-edicao@example.com',
            cpf='39053344705',
            data_nascimento='2001-03-04',
            telefone='11912345678',
            disponibilidade='tarde',
            status='pendente',
            observacoes='Matricula usada para teste de edicao.',
        )

        aula = Aula.objects.create(
            data=timezone.localdate() + timedelta(days=7),
            horario='09:00',
            topico='Aula Cypress'
        )
        Presenca.objects.create(
            aula=aula,
            inscricao=inscricao,
            presente=True
        )

        produto = Produto.objects.create(
            nome='Bolsa Cypress',
            descricao='Produto artesanal para teste Cypress.',
            preco='79.90',
            categoria='Bolsas',
            ativo=True
        )
        ProdutoImagem.objects.create(
            produto=produto,
            nome='bolsa-cypress.png',
            tipo='image/png',
            conteudo=b'imagem-cypress',
            ordem=0,
        )

        Servico.objects.create(
            nome='Ajuste Cypress',
            descricao='Servico de costura para teste Cypress.',
            tipo='Costura',
            ativo=True
        )

        SolicitacaoContato.objects.create(
            tipo='doacao',
            nome='Contato Cypress',
            email='contato-cypress@example.com',
            telefone='11900000000',
            mensagem='Contato criado para teste Cypress.'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Dados Cypress preparados: admin={admin.email}, aluna={aluna.email}, inscricao={inscricao.id}'
            )
        )
