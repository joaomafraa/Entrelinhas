<p align="center">
  <img src="assets/LOGO%20ENTRELINHAS_page-0001.jpg" alt="Logo EntreLinhas" width="360">
</p>

# EntreLinhas

Plataforma digital para inscricao em cursos de costura, acompanhamento de alunas, gestao administrativa e bazar solidario.

## Sobre

O EntreLinhas centraliza os principais fluxos da ONG em uma unica aplicacao:

- inscricao e acompanhamento de matriculas;
- area da aluna com aulas, frequencia e certificado;
- painel administrativo para inscricoes, aulas, certificados, suporte, produtos, servicos, doacoes e parcerias;
- bazar publico com produtos e servicos;
- apoio por PIX, WhatsApp e formulario de contato.

## Links

- [Prototipo no Figma LO-FI](https://www.figma.com/design/h6YsEeVpd3D9KYrYruWpGY/Lo-fi-epicos?node-id=29-159&t=2rZ7MKiQh6C3mTaF-1)
- [Prototipo no Figma HI-FI](https://www.figma.com/file/bwWHMEyJaw1yB2yQbOPtrL?node-id=0:1&locale=pt-br&type=design)
- [Documentacao no Google Sites](https://sites.google.com/cesar.school/entrelinhas/home)
- [Gestao do Projeto no Jira](https://cesar-team-n9qvr2he.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog?epics=visible&jql=parent%20IN%20%28SCRUM-8%2C%20SCRUM-9%2C%20SCRUM-10%29&selectedIssue=SCRUM-8)
- [Deploy](https://entrelinhas-e759.onrender.com)
- [screencast E2E](https://youtu.be/iwpXMyesjmQ)
- [screencast ci/cd](https://youtu.be/EKdjPhmJ4w8)
- [screencast Deploy final](https://youtu.be/Ig0aF1VkaJU)

## Funcionalidades

### Inscricao e matricula

- Cadastro de conta e login.
- Formulario de inscricao com validacao de CPF, telefone e campos obrigatorios.
- Listagem administrativa de inscricoes.
- Edicao e cancelamento de matricula pela aluna.
- Atualizacao de status da inscricao pelo administrador.

### Acompanhamento

- Cadastro e edicao de aulas.
- Calendario de aulas.
- Registro de presenca.
- Area da aluna com frequencia, proximas aulas, perfil e certificados.
- Upload, liberacao e download de certificado.

### Bazar e apoio

- Cadastro administrativo de produtos e servicos.
- Upload de imagem principal e galeria.
- Vitrine publica com busca e filtros.
- Link de interesse via WhatsApp com mensagem pronta.
- Pagina Apoiar com PIX e formulario de doacao/parceria.
- Painel administrativo para suporte, doacoes e parcerias.
- Cadastro da chave PIX pelo painel administrativo.

## Historias de Usuario

As historias foram organizadas por epico e cobertas por testes Django e Cypress.

<details>
<summary>Epico 1 - Inscricao e Matricula</summary>

### H1 - Inscricao no curso

Como aluna, quero me inscrever no curso preenchendo um formulario para garantir minha participacao.

**Cenarios BDD**

- Cenario 1: Inscricao com dados validos
  - Dado que estou na pagina de inscricao
  - Quando preencho todos os dados obrigatorios corretamente
  - E seleciono minha disponibilidade
  - E envio o formulario
  - Entao minha inscricao deve ser registrada com sucesso

- Cenario 2: Campos obrigatorios vazios ou invalidos
  - Dado que estou na pagina de inscricao
  - Quando tento enviar o formulario com campos obrigatorios vazios ou invalidos
  - Entao devo receber mensagens de erro
  - E a inscricao nao deve ser concluida

- Cenario 3: Letras em campos numericos
  - Dado que informo letras em campos que devem receber numeros, como CPF ou telefone
  - Quando tento enviar o formulario
  - Entao devo receber uma mensagem informativa indicando que o campo deve conter apenas numeros
  - E a inscricao nao deve ser concluida

### H2 - Gerenciar inscricoes

Como administrador, quero visualizar as inscricoes realizadas para acompanhar e organizar as alunas do curso.

**Cenarios BDD**

- Cenario 1: Visualizar inscricoes existentes
  - Dado que existem inscricoes registradas
  - Quando o administrador acessa a lista de inscricoes
  - Entao deve visualizar os dados das alunas cadastradas

- Cenario 2: Lista sem inscricoes
  - Dado que nao existem inscricoes cadastradas
  - Quando o administrador acessa a lista de inscricoes
  - Entao deve ver uma mensagem informativa

- Cenario 3: Visualizar dados da inscricao
  - Dado que existe uma inscricao registrada
  - Quando o administrador acessa a listagem
  - Entao deve ver nome, e-mail, telefone, CPF e status da inscricao

### H3 - Gerenciar matricula

Como aluna, quero editar ou cancelar minha matricula para manter meus dados atualizados ou desistir do curso.

**Cenarios BDD**

- Cenario 1: Editar matricula com dados validos
  - Dado que tenho uma matricula ativa
  - Quando acesso meus dados
  - E realizo alteracoes validas
  - Entao minhas informacoes devem ser atualizadas

- Cenario 2: Cancelar matricula
  - Dado que tenho uma matricula ativa
  - Quando solicito o cancelamento
  - E confirmo a acao
  - Entao minha matricula deve ser cancelada

- Cenario 3: Salvar dados invalidos
  - Dado que estou editando minha matricula
  - Quando tento salvar dados invalidos
  - Entao devo receber mensagem de erro
  - E meus dados nao devem ser atualizados incorretamente

</details>

<details>
<summary>Epico 2 - Acompanhamento da Aluna</summary>

### H1 - Registrar presenca

Como administrador ou instrutor, quero registrar presenca das alunas para acompanhar a frequencia.

**Cenarios BDD**

- Cenario 1: Registrar presenca
  - Dado que existe uma aula cadastrada
  - Quando o administrador marca presenca de uma aluna
  - Entao a presenca deve ser registrada

- Cenario 2: Manter status salvo
  - Dado que a presenca ja foi registrada
  - Quando o administrador acessa a aula novamente
  - Entao deve ver o status de presenca salvo

- Cenario 3: Registrar falta
  - Dado que existe uma aula cadastrada
  - Quando a aluna nao e marcada como presente
  - Entao a aula deve aparecer como falta na area da aluna

### H2 - Gerenciar calendario de aulas

Como administrador ou instrutor, quero cadastrar e atualizar aulas no calendario para organizar os horarios do curso.

**Cenarios BDD**

- Cenario 1: Criar aula
  - Dado que estou no painel administrativo
  - Quando cadastro uma aula com data, horario e topico
  - Entao ela deve aparecer na lista e no calendario de aulas

- Cenario 2: Editar aula
  - Dado que existe uma aula cadastrada
  - Quando altero seus dados e salvo
  - Entao o calendario deve exibir as informacoes atualizadas

- Cenario 3: Dados invalidos
  - Dado que estou cadastrando ou editando uma aula
  - Quando informo data ou horario invalidos
  - Entao o sistema deve impedir o salvamento e exibir erro

### H3 - Gerar certificado

Como administrador, quero liberar certificados para que alunas concluintes comprovem participacao no curso.

**Cenarios BDD**

- Cenario 1: Liberar certificado
  - Dado que a aluna concluiu o curso e possui certificado cadastrado
  - Quando o administrador libera o certificado
  - Entao a aluna deve conseguir visualiza-lo na area da aluna

- Cenario 2: Certificado nao liberado
  - Dado que a aluna ainda nao possui certificado liberado
  - Quando acessa a area de certificados
  - Entao o certificado nao deve estar disponivel

- Cenario 3: Baixar certificado liberado
  - Dado que o certificado foi liberado com arquivo valido
  - Quando a aluna solicita o download
  - Entao o arquivo do certificado deve ser baixado

### H4 - area da aluna liberada

Como usuaria, quero ver a area mais relevante conforme minha matricula para acessar rapidamente acompanhamento, inscricao ou bazar.

**Cenarios BDD**

- Cenario 1: Aluna matriculada
  - Dado que a usuaria esta matriculada no curso
  - Quando realiza login no sistema
  - Entao a area de acompanhamento deve ser liberada

- Cenario 2: Usuaria sem matricula
  - Dado que a usuaria nao possui matricula
  - Quando realiza login no sistema
  - Entao deve ser orientada para inscricao ou bazar

- Cenario 3: Visitante nao logada
  - Dado que a visitante nao esta logada
  - Quando acessa a plataforma
  - Entao deve conseguir visualizar a area publica e o bazar

</details>

<details>
<summary>Epico 3 - Bazar, Doacoes e Parcerias</summary>

### H1 - Cadastro de produtos e servicos

Como administrador, quero cadastrar produtos e servicos no bazar para disponibilizar itens e servicos da ONG.

**Cenarios BDD**

- Cenario 1: Cadastro de item no bazar
  - Dado que sou administrador da plataforma
  - Quando acesso a area de cadastro do bazar
  - E preencho os dados de um produto ou servico corretamente
  - Entao o item deve ser registrado no bazar

- Cenario 2: Cadastro de produto ou servico
  - Dado que estou cadastrando um produto
  - Quando informo nome, descricao, preco, categoria, imagem e WhatsApp invalidos
  - Entao o usuario deve ser notificado

- Cenario 3: Cadastro de servico
  - Dado que estou cadastrando um servico
  - Quando informo nome, descricao, tipo, imagem e status ativo
  - Entao o servico deve ser salvo corretamente

### H2 - Vitrine de produtos e servicos

Como visitante, quero visualizar e filtrar produtos e servicos para encontrar itens de interesse.

**Cenarios BDD**

- Cenario 1: Visualizar itens ativos
  - Dado que existem produtos e servicos ativos
  - Quando acesso a vitrine publica do bazar
  - Entao devo visualizar os itens disponiveis

- Cenario 2: Filtrar itens
  - Dado que estou na vitrine do bazar
  - Quando aplico busca ou filtro por tipo
  - Entao devo ver apenas os itens correspondentes

- Cenario 3: Nenhum resultado encontrado
  - Dado que aplico um filtro sem resultados
  - Quando a lista e atualizada
  - Entao devo ver uma mensagem informativa

### H3 - Gerenciamento de doacoes e parcerias

Como administrador, quero visualizar e gerenciar contatos de doacoes e parcerias para acompanhar solicitacoes recebidas.

**Cenarios BDD**

- Cenario 1: Visualizar contatos recebidos
  - Dado que existem formularios de doacao ou parceria enviados
  - Quando o administrador acessa a area de Doacoes e Parcerias
  - Entao deve visualizar a lista de pessoas que entraram em contato

- Cenario 2: Visualizar daodos do formulario
  - Dado que nao existe contato registrado
  - Quando o administrador consulta a lista
  - Entao o sistema deve informar o administrador

- Cenario 3: Atualizar status da solicitacao
  - Dado que estou na lista de contatos
  - Quando altero o status de uma solicitacao
  - Entao o status deve ser atualizado corretamente

### H4 - Enviar solicitacao de doacao ou parceria

Como usuario interessado, quero enviar uma solicitacao de doacao ou parceria para apoiar a ONG.

**Cenarios BDD**

- Cenario 1: Enviar solicitacao com sucesso
  - Dado que estou na pagina Apoiar
  - Quando preencho os dados corretamente
  - E envio o formulario
  - Entao a solicitacao deve ser registrada com sucesso

- Cenario 2: Solicitacao de doacao
  - Dado que seleciono a opcao de doacao
  - Quando visualizo a chave PIX
  - E preencho meus dados e mensagem
  - Entao a solicitacao deve ser enviada para analise

- Cenario 3: Solicitacao com dados invalidos
  - Dado que seleciono a opcao de parceria ou doacao 
  - Quando preencho meus dados invalidos
  - Entao o sistema deve notificar

</details>

## Funcionalidades Extras

### WhatsApp no bazar

Produtos podem receber um numero de WhatsApp no cadastro ou edicao. Na pagina de detalhe, o sistema monta um link `wa.me` com mensagem pronta contendo o item de interesse. Se o produto nao tiver numero proprio, o sistema usa `WHATSAPP_CONTATO`; se nenhum numero estiver configurado, o botao fica desativado.

### PIX para doacoes

A pagina Apoiar mostra a chave PIX da ONG quando a opcao de doacao esta selecionada. A chave pode ser cadastrada pelo painel administrativo em `Doacoes e Parcerias`; se nao houver chave salva no banco, o sistema usa `PIX_CHAVE_ONG` como fallback.

### Suporte

A plataforma possui formulario de suporte separado de doacoes e parcerias. As mensagens de suporte aparecem no menu administrativo `Suporte`, enquanto contatos de doacao e parceria aparecem em `Doacoes e Parcerias`.

### Lia - assistente de suporte

A Lia e a assistente virtual da EntreLinhas. Ela aparece nas paginas publicas e na area da aluna para responder duvidas sobre cursos, inscricoes, bazar, formas de apoio e uso da plataforma. Na area da aluna, a Lia tambem pode consultar informacoes reais da matricula, como proxima aula, frequencia atual, presencas, faltas, ultimas aulas faltadas e disponibilidade do certificado.

O contexto enviado para a assistente evita dados sensiveis: CPF, telefone, e-mail, senha e dados bancarios nao sao enviados. A integracao usa a rota `POST /api/chat/` e pode ser configurada por `GROQ_API_KEY`, `GROQ_MODEL` e `GROQ_API_URL`.

### JavaScript

O JavaScript foi usado para copiar PIX, controlar interacoes do suporte, confirmar exclusoes administrativas, enviar alteracoes de status automaticamente e apoiar o cadastro de imagens no bazar.

## Como Rodar

### 1. Clonar o projeto

```bash
git clone LINK_DO_REPOSITORIO
cd EntreLinhas
```

### 2. Criar e ativar ambiente virtual

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 4. Configurar ambiente

Crie um arquivo `.env` a partir do `.env.example` e preencha os valores necessarios.

Variaveis principais:

```text
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
WHATSAPP_CONTATO=
PIX_CHAVE_ONG=
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
```

### 5. Rodar migrations

```bash
python manage.py migrate
```

### 6. Criar superusuario

```bash
python manage.py createsuperuser
```

### 7. Subir servidor

```bash
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

Painel administrativo da plataforma:

```text
http://127.0.0.1:8000/inscricao/dashboard/
```

Admin nativo do Django:

```text
http://127.0.0.1:8000/admin/
```

## Testes

### Django

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --verbosity 2
```

### Cypress

Instale as dependencias Node:

```bash
npm ci
```

Rodar suite E2E:

```bash
npm run cy:run
```

Abrir interface visual:

```bash
npm run cy:open
```

Abrir interface visual lenta:

```bash
npm run cy:open:slow
```

Rodar um spec especifico:

```bash
node tools/run_cypress.js --spec cypress/e2e/inscricoes/epico3/bazar_produtos_servicos_doacoes_parcerias.cy.js
```

## CI/CD

O projeto usa GitHub Actions em `.github/workflows/ci-cd.yml`.

Em push ou pull request para `main`, o workflow executa:

- Unit and integration tests;
- Build validation;
- Cypress end-to-end tests;
- Deploy Render em push para `main`.

Configure os secrets no GitHub Actions:

```text
DJANGO_SECRET_KEY
RENDER_DEPLOY_HOOK_URL
```

Variaveis recomendadas no Render:

```text
SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://seu-app.onrender.com
DATABASE_URL=postgresql://...
DJANGO_SUPERUSER_EMAIL=admin@entrelinhas.com
DJANGO_SUPERUSER_PASSWORD=sua-senha
DJANGO_SUPERUSER_NAME=Nome Admin
WHATSAPP_CONTATO=
PIX_CHAVE_ONG=
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
```

Build command:

```bash
bash build.sh
```

Start command:

```bash
gunicorn configuracoes.wsgi:application
```

## Estrutura do Projeto

```text
EntreLinhas/
├── configuracoes/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── inscricoes/
│   ├── management/commands/
│   │   ├── ensure_admin.py
│   │   └── seed_cypress.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── bazar/
│   ├── certificados/
│   └── inscricoes/
├── static/
│   ├── assets/icons/
│   ├── css/
│   └── js/
├── tests/
│   └── test_historias.py
├── cypress/
│   ├── e2e/inscricoes/
│   └── support/
├── tools/
│   └── run_cypress.js
├── .github/workflows/
│   └── ci-cd.yml
├── build.sh
├── manage.py
├── package.json
├── requirements.txt
└── README.md
```

## Entregas

<details>
<summary>Ver entregas</summary>

<details>
<summary>Semana 1 - Inscricao no curso</summary>

- Implementacao do epico de inscricao do curso com suas funcionalidades.
- Cadastro de conta e login.
- Formulario de inscricao.
- Gerenciamento administrativo das inscricoes.
- Edicao e cancelamento de matricula.

</details>

<details>
<summary>Semana 2 - Acompanhamento da aluna</summary>

- Implementacao da area da aluna.
- Cadastro e gerenciamento de aulas.
- Registro de presenca.
- Calendario de aulas e frequencia.
- Liberacao e download de certificados.

</details>

<details>
<summary>Semana 3 - Bazar, doacoes e parcerias</summary>

- Cadastro de produtos e servicos do bazar.
- Vitrine publica com busca e filtros.
- Contato via WhatsApp para produtos.
- Formulario de doacao e parceria.
- Painel administrativo para doacoes, parcerias e chave PIX.

</details>

<details>
<summary>Semana 4 - Ajustes finais</summary>

- Revisao dos fluxos principais da plataforma.
- Ajustes finais de interface e organizacao administrativa.
- Ajustes nos testes automatizados.
- Atualizacao da documentacao do projeto.

</details>

</details>

## Pair Programming e Revisao de Codigo

A tecnica de Pair Programming nao foi utilizada como pratica principal durante o desenvolvimento porque a equipe dividiu o sistema em modulos independentes, como inscricoes, acompanhamento da aluna, bazar, suporte, testes e documentacao. Essa organizacao permitiu que cada integrante trabalhasse em entregas especificas, respeitando diferentes horarios de disponibilidade e evitando bloqueios entre tarefas que nao dependiam diretamente uma da outra.

Mesmo sem pareamento continuo em tempo real, a equipe manteve colaboracao tecnica por meio de revisao de codigo, validacao cruzada das funcionalidades e alinhamento dos criterios de aceite definidos nas historias de usuario. Assim, as implementacoes foram conferidas por outros membros antes da consolidacao, garantindo consistencia entre requisitos, testes, interface e comportamento esperado do sistema.

## Tecnologias

- Python 3
- Django 6
- SQLite em desenvolvimento
- PostgreSQL no deploy via `DATABASE_URL`
- WhiteNoise para arquivos estaticos
- Gunicorn como servidor WSGI em producao
- Render para deploy
- GitHub Actions para CI/CD
- HTML, CSS e JavaScript
- Bootstrap 5
- Cypress para testes E2E
- Node.js e npm para automacao dos testes Cypress
- Groq API para suporte virtual configuravel

## Contribuicao

Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Autores

- João Carlos Mafra - jcmsn@cesar.school
- Laura Vitória - lvsa@gmail.com
- Marina Marinho - mmm3@cesar.school
- Márcio Rodrigues Perez - mrpf@cesar.school
- Ivan Pinto - iprf@cesar.school
- Gabriel Tabosa - ggt2@cesar.school
- Pedro José - pjos@cesar.school
- João Neto - jffn@cesar.school
- Clara Kyrillos - crk@cesar.school
- Guilherme Lira - gmcl@cesar.school
- Luísa Feitosa Magalhães - lfm3@cesar.school
