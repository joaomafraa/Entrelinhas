# Guia de Contribuicao

Este guia descreve como contribuir com o projeto EntreLinhas mantendo o fluxo de desenvolvimento, testes e deploy organizado.

## Fluxo recomendado

1. Atualize a branch principal:

```bash
git checkout main
git pull origin main
```

2. Crie uma branch para a alteracao:

```bash
git checkout -b feature/nome-da-funcionalidade
```

Use nomes curtos e claros, por exemplo:

```text
feature/dashboard-admin
fix/cypress-epico-3
fix/chave-pix-admin
```

3. Implemente a alteracao com escopo pequeno.

4. Rode os testes antes de abrir pull request.

5. Abra pull request para `main`.

## Padrao de commits

Use mensagens curtas e objetivas:

```text
ajusta testes do epico 3
cria cadastro de chave pix
corrige dashboard admin
```

Evite commits grandes misturando assuntos diferentes.

## Ambiente local

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale dependencias:

```bash
pip install -r requirements.txt
npm ci
```

Crie o `.env` a partir do `.env.example`.

Nunca suba `.env`, chaves reais, senhas ou tokens para o GitHub.

## Migrations

Sempre crie migrations quando alterar modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

Antes de finalizar, confira se nao existem migrations pendentes:

```bash
python manage.py makemigrations --check --dry-run
```

## Testes

Rode as validacoes Django:

```bash
python manage.py check
python manage.py test tests --verbosity 2
```

Rode os testes E2E:

```bash
npm run cy:run
```

Para testar apenas um epico:

```bash
node tools/run_cypress.js --spec cypress/e2e/inscricoes/epico3/bazar_produtos_servicos_doacoes_parcerias.cy.js
```

Para acompanhar visualmente:

```bash
npm run cy:open:slow
```

## Cypress

Os testes Cypress ficam em:

```text
cypress/e2e/inscricoes/
```

Cada spec cobre um epico:

- Epico 1: inscricao, gerenciamento e matricula.
- Epico 2: aulas, presenca, certificados e area da aluna.
- Epico 3: bazar, doacoes e parcerias.

Evite usar o admin nativo do Django nos testes E2E quando existir uma tela propria da plataforma. O teste deve representar o fluxo real do usuario ou administrador.

## Estilo de implementacao

- Prefira os padroes ja usados no projeto.
- Mantenha alteracoes pequenas e relacionadas ao objetivo da branch.
- Evite refatoracoes grandes junto com bugfixes simples.
- Use mensagens de erro claras para o usuario.
- Mantenha formularios, templates e estilos consistentes com o painel existente.

## Deploy

O deploy roda pelo GitHub Actions e Render.

Antes de enviar para `main`, confirme:

- migrations criadas e aplicadas localmente;
- testes Django passando;
- Cypress passando;
- nenhuma chave real em arquivos versionados;
- `.env.example` atualizado quando houver variavel nova.

## Checklist de pull request

- [ ] Alteracao resolve o problema descrito.
- [ ] `python manage.py check` passou.
- [ ] `python manage.py makemigrations --check --dry-run` passou.
- [ ] `python manage.py test tests --verbosity 2` passou.
- [ ] `npm run cy:run` passou ou foi justificado.
- [ ] Nao ha secrets no commit.
- [ ] README ou documentacao foram atualizados quando necessario.
