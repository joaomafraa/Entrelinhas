from django import forms
from .models import Inscricao


class InscricaoForm(forms.ModelForm):

    class Meta:

        model = Inscricao

        fields = [
            'nome',
            'email',
            'telefone',
            'disponibilidade',
            'observacoes',
        ]

        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
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

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Digite seu e-mail'
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