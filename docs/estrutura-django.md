# Estrutura Django

Este projeto foi organizado para iniciar o desenvolvimento em Django sem implementar funcionalidades neste momento.

## Separacao por apps

- `core`: codigo compartilhado entre os demais apps.
- `usuarios`: autenticacao, perfis e permissoes futuramente.
- `inscricoes`: inscricao no curso e matricula.
- `acompanhamento`: aulas, presencas e certificados.
- `bazar`: produtos, servicos, doacoes, parcerias e contatos.

## Arquivos principais

- `manage.py`: utilitario de comandos do Django.
- `config/settings.py`: configuracoes gerais do projeto.
- `config/urls.py`: rotas principais.
- `requirements.txt`: dependencias Python.
- `.env.example`: exemplo das variaveis de ambiente.

## Observacao

As pastas foram criadas somente para organizar o inicio do projeto. Modelos, views, forms, templates e regras de negocio devem ser adicionados nas proximas etapas.
