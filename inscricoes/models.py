from django.conf import settings
from django.db import models
from django.utils import timezone


class Inscricao(models.Model):

    DISPONIBILIDADE = (
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
    )

    STATUS = (
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('recusada', 'Recusada'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscricoes',
        blank=True,
        null=True
    )

    nome = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    cpf = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True
    )

    data_nascimento = models.DateField(
        blank=True,
        null=True
    )

    telefone = models.CharField(
        max_length=20
    )

    disponibilidade = models.CharField(
        max_length=20,
        choices=DISPONIBILIDADE
    )

    observacoes = models.TextField(
        blank=True,
        null=True
    )

    ativa = models.BooleanField(
        default=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pendente'
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    curso_concluido = models.BooleanField(
        default=False
    )

    certificado_liberado = models.BooleanField(
        default=False
    )

    certificado_liberado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    certificado_nome_arquivo = models.CharField(
        max_length=255,
        blank=True
    )

    certificado_tipo_arquivo = models.CharField(
        max_length=100,
        blank=True
    )

    certificado_conteudo = models.BinaryField(
        blank=True,
        null=True,
        editable=False
    )

    @property
    def idade(self):

        if not self.data_nascimento:

            return None

        hoje = timezone.localdate()

        return (
            hoje.year
            - self.data_nascimento.year
            - (
                (hoje.month, hoje.day)
                < (self.data_nascimento.month, self.data_nascimento.day)
            )
        )

    @property
    def cpf_formatado(self):

        if not self.cpf or len(self.cpf) != 11:

            return self.cpf or ''

        return f'{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}'

    @property
    def certificado_disponivel(self):

        return self.certificado_liberado and bool(self.certificado_conteudo)

    @property
    def frequencia_percentual(self):

        total_aulas = Aula.objects.filter(
            data__lte=timezone.localdate()
        ).count()

        if total_aulas == 0:

            return 0

        presencas_confirmadas = Presenca.objects.filter(
            inscricao=self,
            aula__data__lte=timezone.localdate(),
            presente=True
        ).count()

        return round((presencas_confirmadas / total_aulas) * 100)

    @property
    def frequencia_classe(self):

        frequencia = self.frequencia_percentual

        if frequencia < 50:

            return 'baixa'

        if frequencia <= 70:

            return 'media'

        return 'alta'

    def __str__(self):
        return self.nome
    
    def concluiu_curso(self):

        if self.status != 'aprovada':
            return False

        return self.curso_concluido or self.frequencia_percentual >= 75


class Aula(models.Model):

    data = models.DateField()

    horario = models.TimeField()

    topico = models.CharField(
        max_length=150,
        blank=True
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-data', '-horario', '-data_criacao']

    def __str__(self):

        if self.topico:

            return f'{self.data:%d/%m/%Y} {self.horario:%H:%M} - {self.topico}'

        return f'{self.data:%d/%m/%Y} {self.horario:%H:%M}'


class Presenca(models.Model):

    aula = models.ForeignKey(
        Aula,
        on_delete=models.CASCADE
    )

    inscricao = models.ForeignKey(
        Inscricao,
        on_delete=models.CASCADE
    )

    presente = models.BooleanField(
        default=False
    )

    registrada_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('aula', 'inscricao')


class Produto(models.Model):

    nome = models.CharField(max_length=120)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=80)
    whatsapp_contato = models.CharField(max_length=20, blank=True)
    imagem_nome = models.CharField(max_length=255, blank=True)
    imagem_tipo = models.CharField(max_length=100, blank=True)
    imagem_conteudo = models.BinaryField(blank=True, null=True, editable=False)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']

    @property
    def tem_imagem(self):

        return self.imagens.exists() or bool(self.imagem_conteudo)

    @property
    def imagem_capa(self):

        return self.imagens.order_by('ordem', 'id').first()

    @property
    def preco_formatado(self):

        return f'R$ {self.preco:.2f}'.replace('.', ',')

    def __str__(self):
        return self.nome


class ProdutoImagem(models.Model):

    produto = models.ForeignKey(
        Produto,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=100)
    conteudo = models.BinaryField(editable=False)
    ordem = models.PositiveIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.nome


class Servico(models.Model):

    nome = models.CharField(max_length=120)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo = models.CharField(max_length=80)
    imagem_nome = models.CharField(max_length=255, blank=True)
    imagem_tipo = models.CharField(max_length=100, blank=True)
    imagem_conteudo = models.BinaryField(blank=True, null=True, editable=False)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']

    @property
    def tem_imagem(self):

        return self.imagens.exists() or bool(self.imagem_conteudo)

    @property
    def imagem_capa(self):

        return self.imagens.order_by('ordem', 'id').first()

    @property
    def preco_formatado(self):

        return f'R$ {self.preco:.2f}'.replace('.', ',')

    def __str__(self):
        return self.nome


class ServicoImagem(models.Model):

    servico = models.ForeignKey(
        Servico,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=100)
    conteudo = models.BinaryField(editable=False)
    ordem = models.PositiveIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.nome


class SolicitacaoContato(models.Model):

    TIPO = (
        ('doacao', 'Doacao'),
        ('parceria', 'Parceria'),
        ('suporte', 'Suporte'),
    )

    STATUS = (
        ('nova', 'Nova'),
        ('em_analise', 'Em analise'),
        ('respondida', 'Respondida'),
        ('arquivada', 'Arquivada'),
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO
    )

    nome = models.CharField(
        max_length=120
    )

    email = models.EmailField()

    telefone = models.CharField(
        max_length=20
    )

    mensagem = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='nova'
    )

    criada_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizada_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.nome}'
