from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone

from .models import Aula, Inscricao, Produto, Servico, SolicitacaoContato


User = get_user_model()

CERTIFICADO_EXTENSOES_PERMITIDAS = {'.pdf', '.jpg', '.jpeg', '.png'}
CERTIFICADO_TAMANHO_MAXIMO = 10 * 1024 * 1024
BAZAR_IMAGEM_EXTENSOES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.webp'}
BAZAR_IMAGEM_TAMANHO_MAXIMO = 5 * 1024 * 1024


class MultipleFileInput(forms.ClearableFileInput):

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):

    def clean(self, data, initial=None):

        files = data if isinstance(data, (list, tuple)) else [data] if data else []

        return [
            super(MultipleFileField, self).clean(file, initial)
            for file in files
            if file
        ]


def normalizar_cpf(cpf):

    return ''.join(caractere for caractere in cpf if caractere.isdigit())


def normalizar_telefone(telefone):

    return ''.join(caractere for caractere in telefone if caractere.isdigit())


def cpf_valido(cpf):

    cpf = normalizar_cpf(cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:

        return False

    for tamanho in (9, 10):

        soma = sum(
            int(cpf[indice]) * ((tamanho + 1) - indice)
            for indice in range(tamanho)
        )

        digito = (soma * 10) % 11

        if digito == 10:

            digito = 0

        if digito != int(cpf[tamanho]):

            return False

    return True


class CadastroForm(forms.Form):

    nome = forms.CharField(
        label='Nome completo',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Digite seu nome'
            }
        )
    )

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'voce@exemplo.com',
                'autocomplete': 'email'
            }
        )
    )

    senha = forms.CharField(
        label='Senha',
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Crie uma senha',
                'autocomplete': 'new-password'
            }
        )
    )

    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Repita sua senha',
                'autocomplete': 'new-password'
            }
        )
    )

    def clean_email(self):

        email = self.cleaned_data['email'].lower()

        if User.objects.filter(username=email).exists():

            raise forms.ValidationError('Já existe uma conta com este e-mail.')

        return email

    def clean(self):

        cleaned_data = super().clean()

        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if senha and confirmar_senha and senha != confirmar_senha:

            self.add_error(
                'confirmar_senha',
                'As senhas não conferem.'
            )

        return cleaned_data

    def save(self):

        nome = self.cleaned_data['nome'].strip()
        email = self.cleaned_data['email']
        first_name, _, last_name = nome.partition(' ')

        return User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['senha'],
            first_name=first_name,
            last_name=last_name
        )


class LoginForm(forms.Form):

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'voce@exemplo.com',
                'autocomplete': 'username'
            }
        )
    )

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '********',
                'autocomplete': 'current-password'
            }
        )
    )

    def __init__(self, request=None, *args, **kwargs):

        self.request = request
        self.user = None

        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        senha = cleaned_data.get('senha')

        if email and senha:

            self.user = authenticate(
                self.request,
                username=email.lower(),
                password=senha
            )

            if self.user is None:

                raise forms.ValidationError('E-mail ou senha inválidos.')

        return cleaned_data


class InscricaoForm(forms.ModelForm):

    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'inputmode': 'numeric'
            }
        ),
        error_messages={
            'required': 'Informe o CPF.'
        }
    )

    class Meta:

        model = Inscricao

        fields = [
            'nome',
            'cpf',
            'data_nascimento',
            'telefone',
            'disponibilidade',
            'observacoes',
        ]

        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'data_nascimento': 'Data de nascimento',
            'telefone': 'Telefone',
            'disponibilidade': 'Disponibilidade',
            'observacoes': 'Observações',
        }

        widgets = {

            'nome': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Digite seu nome'
                }
            ),

            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'telefone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '(00) 00000-0000',
                    'inputmode': 'numeric'
                }
            ),

            'disponibilidade': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'observacoes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Observações opcionais',
                    'rows': 4
                }
            ),
        }

        error_messages = {
            'nome': {
                'required': 'Informe o nome completo.',
            },
            'data_nascimento': {
                'required': 'Informe a data de nascimento.',
                'invalid': 'Informe uma data de nascimento valida.',
            },
            'telefone': {
                'required': 'Informe o telefone.',
            },
            'disponibilidade': {
                'required': 'Selecione a disponibilidade.',
            },
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['cpf'].required = True
        self.fields['data_nascimento'].required = True

    def clean_cpf(self):

        cpf = normalizar_cpf(self.cleaned_data['cpf'])

        if not cpf_valido(cpf):

            raise forms.ValidationError('Informe um CPF válido.')

        inscricao_com_cpf = Inscricao.objects.filter(cpf=cpf)

        if self.instance and self.instance.pk:

            inscricao_com_cpf = inscricao_com_cpf.exclude(pk=self.instance.pk)

        if inscricao_com_cpf.exists():

            raise forms.ValidationError('Este CPF já está vinculado a outra inscrição.')

        return cpf

    def clean_data_nascimento(self):

        data_nascimento = self.cleaned_data['data_nascimento']

        if not data_nascimento:

            raise forms.ValidationError('Informe a data de nascimento.')

        if data_nascimento > timezone.localdate():

            raise forms.ValidationError('A data de nascimento não pode ser futura.')

        return data_nascimento

    def clean_telefone(self):

        telefone = self.cleaned_data['telefone'].strip()
        caracteres_permitidos = set('0123456789 ()-+.')

        if any(caractere not in caracteres_permitidos for caractere in telefone):

            raise forms.ValidationError('O telefone deve conter apenas numeros.')

        telefone_normalizado = normalizar_telefone(telefone)

        if len(telefone_normalizado) < 10 or len(telefone_normalizado) > 11:

            raise forms.ValidationError('Informe um telefone valido com DDD.')

        return telefone_normalizado


class AdminInscricaoForm(InscricaoForm):

    class Meta(InscricaoForm.Meta):

        fields = InscricaoForm.Meta.fields + [
            'status',
        ]

        labels = {
            **InscricaoForm.Meta.labels,
            'status': 'Status da matricula',
        }

        widgets = {
            **InscricaoForm.Meta.widgets,
            'status': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
        }


class CertificadoUploadForm(forms.Form):

    certificado_arquivo = forms.FileField(
        label='Arquivo do certificado',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png'
            }
        )
    )

    def clean_certificado_arquivo(self):

        arquivo = self.cleaned_data.get('certificado_arquivo')

        if not arquivo:

            raise forms.ValidationError('Anexe o arquivo do certificado.')

        nome = arquivo.name.lower()

        if not any(nome.endswith(extensao) for extensao in CERTIFICADO_EXTENSOES_PERMITIDAS):

            raise forms.ValidationError('Envie um arquivo PDF, JPG, JPEG ou PNG.')

        if arquivo.size > CERTIFICADO_TAMANHO_MAXIMO:

            raise forms.ValidationError('O arquivo deve ter no maximo 10 MB.')

        return arquivo


class AulaForm(forms.ModelForm):

    class Meta:

        model = Aula

        fields = [
            'data',
            'horario',
            'topico',
        ]

        labels = {
            'data': 'Data da aula',
            'horario': 'Horario',
            'topico': 'Tópico',
        }

        widgets = {

            'data': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'horario': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),

            'topico': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex.: Introdução à máquina de costura'
                }
            ),
        }

        error_messages = {
            'data': {
                'required': 'Informe a data da aula.',
                'invalid': 'Informe uma data válida.',
            },
            'horario': {
                'required': 'Informe o horario da aula.',
                'invalid': 'Informe um horario valido.',
            },
        }

    def clean_data(self):

        data = self.cleaned_data['data']

        if not self.instance.pk and data < timezone.localdate():

            raise forms.ValidationError('A data da aula nao pode ser passada.')

        return data


class BazarItemForm(forms.ModelForm):

    imagem = MultipleFileField(
        label='Imagens',
        required=False,
        widget=MultipleFileInput(
            attrs={
                'class': 'bazar-file-input',
                'accept': '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp',
                'multiple': True,
            }
        )
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not self.instance.pk or not self.instance.tem_imagem:

            self.fields['imagem'].required = True

    def clean_preco(self):

        preco = self.cleaned_data['preco']

        if preco <= 0:

            raise forms.ValidationError('Informe um valor maior que zero.')

        return preco

    def clean_imagem(self):

        imagens = self.cleaned_data.get('imagem') or []

        if not imagens:

            if self.instance.pk and self.instance.tem_imagem:

                return imagens

            raise forms.ValidationError('Anexe pelo menos uma imagem.')

        for imagem in imagens:

            nome = imagem.name.lower()

            if not any(nome.endswith(extensao) for extensao in BAZAR_IMAGEM_EXTENSOES_PERMITIDAS):

                raise forms.ValidationError('Envie apenas imagens JPG, JPEG, PNG ou WEBP.')

            if imagem.size > BAZAR_IMAGEM_TAMANHO_MAXIMO:

                raise forms.ValidationError('Cada imagem deve ter no maximo 5 MB.')

        return imagens


class ProdutoForm(BazarItemForm):

    class Meta:

        model = Produto
        fields = [
            'nome',
            'descricao',
            'preco',
            'categoria',
            'whatsapp_contato',
            'ativo',
        ]
        labels = {
            'nome': 'Nome',
            'descricao': 'Descricao',
            'preco': 'Valor',
            'categoria': 'Categoria',
            'whatsapp_contato': 'WhatsApp de contato',
            'ativo': 'Ativo',
        }
        help_texts = {
            'whatsapp_contato': 'Opcional. Use DDI, DDD e numero. Ex.: 5581999999999',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Bolsa de tecido'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o produto'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Bolsas'}),
            'whatsapp_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: 5581999999999'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_whatsapp_contato(self):

        whatsapp_contato = self.cleaned_data.get('whatsapp_contato', '').strip()

        if not whatsapp_contato:

            return ''

        whatsapp_contato = normalizar_telefone(whatsapp_contato)

        if len(whatsapp_contato) < 12 or len(whatsapp_contato) > 13:

            raise forms.ValidationError('Informe o WhatsApp com DDI, DDD e numero.')

        return whatsapp_contato


class ServicoForm(BazarItemForm):

    class Meta:

        model = Servico
        fields = [
            'nome',
            'descricao',
            'tipo',
            'ativo',
        ]
        labels = {
            'nome': 'Nome',
            'descricao': 'Descricao',
            'tipo': 'Tipo de servico',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Ajuste de roupa'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o servico'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Costura'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SolicitacaoContatoForm(forms.ModelForm):

    class Meta:

        model = SolicitacaoContato
        fields = [
            'tipo',
            'nome',
            'email',
            'telefone',
            'mensagem',
        ]
        labels = {
            'tipo': 'Tipo de solicitacao',
            'nome': 'Nome completo',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'mensagem': 'Mensagem',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'nome': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Digite seu nome'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'voce@exemplo.com',
                    'autocomplete': 'email'
                }
            ),
            'telefone': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'DDD + telefone',
                    'inputmode': 'numeric',
                    'autocomplete': 'tel'
                }
            ),
            'mensagem': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-lg',
                    'rows': 5,
                    'placeholder': 'Conte como deseja apoiar ou colaborar'
                }
            ),
        }
        error_messages = {
            'tipo': {
                'required': 'Escolha doacao ou parceria.',
                'invalid_choice': 'Escolha uma opcao valida.',
            },
            'nome': {
                'required': 'Informe seu nome.',
            },
            'email': {
                'required': 'Informe seu e-mail.',
                'invalid': 'Informe um e-mail valido.',
            },
            'telefone': {
                'required': 'Informe seu telefone.',
            },
            'mensagem': {
                'required': 'Informe sua mensagem.',
            },
        }

    def clean_telefone(self):

        telefone = self.cleaned_data['telefone'].strip()

        caracteres_permitidos = set('0123456789 ()-+')

        if any(caractere not in caracteres_permitidos for caractere in telefone):

            raise forms.ValidationError('O telefone deve conter apenas numeros.')

        telefone_normalizado = normalizar_telefone(telefone)

        if len(telefone_normalizado) < 10 or len(telefone_normalizado) > 11:

            raise forms.ValidationError('Informe um telefone valido com DDD.')

        return telefone_normalizado


class SuporteContatoForm(SolicitacaoContatoForm):

    class Meta(SolicitacaoContatoForm.Meta):

        fields = [
            'nome',
            'email',
            'telefone',
            'mensagem',
        ]
        labels = {
            'nome': 'Nome completo',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'mensagem': 'Mensagem para o suporte',
        }
        widgets = {
            'nome': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Digite seu nome'
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'voce@exemplo.com',
                    'autocomplete': 'email'
                }
            ),
            'telefone': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'DDD + telefone',
                    'inputmode': 'numeric',
                    'autocomplete': 'tel'
                }
            ),
            'mensagem': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-lg',
                    'rows': 5,
                    'placeholder': 'Conte sua duvida ou problema com a plataforma'
                }
            ),
        }

    def save(self, commit=True):

        solicitacao = super().save(commit=False)
        solicitacao.tipo = 'suporte'

        if commit:

            solicitacao.save()

        return solicitacao
