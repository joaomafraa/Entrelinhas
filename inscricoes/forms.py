from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone

from .models import Inscricao


User = get_user_model()


def normalizar_cpf(cpf):

    return ''.join(caractere for caractere in cpf if caractere.isdigit())


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
        )
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
                    'placeholder': '(00) 00000-0000'
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
