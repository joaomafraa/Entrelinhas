from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0015_produto_whatsapp_contato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaocontato',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('doacao', 'Doacao'),
                    ('parceria', 'Parceria'),
                    ('suporte', 'Suporte'),
                ],
                max_length=20,
            ),
        ),
    ]
