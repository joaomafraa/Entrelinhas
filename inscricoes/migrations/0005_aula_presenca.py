import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0004_inscricao_cpf_inscricao_data_nascimento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('topico', models.CharField(blank=True, max_length=150)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-data', '-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='Presenca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presente', models.BooleanField(default=False)),
                ('registrada_em', models.DateTimeField(auto_now=True)),
                ('aula', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricoes.aula')),
                ('inscricao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricoes.inscricao')),
            ],
            options={
                'unique_together': {('aula', 'inscricao')},
            },
        ),
    ]
