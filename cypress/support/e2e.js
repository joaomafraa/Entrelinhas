Cypress.Commands.add('step', () => {
  if (!Cypress.env('screencast')) {
    return;
  }

  const delay = Number(Cypress.env('stepDelay') || 1500);

  cy.wait(delay);
});

Cypress.Commands.overwrite('type', (originalFn, subject, text, options = {}) => {
  if (Cypress.env('screencast') && options.delay === undefined) {
    const delay = Number(Cypress.env('typeDelay') || 45);

    return originalFn(subject, text, { ...options, delay });
  }

  return originalFn(subject, text, options);
});

Cypress.Commands.add('conclusao', (texto) => {
  cy.log(`Conclusao: ${texto}`);
  cy.step();
});

Cypress.Commands.add('seedCypress', () => {
  cy.exec('python manage.py seed_cypress', {
    env: {
      SECRET_KEY: 'django-insecure-cypress-test-key',
      DEBUG: 'True'
    }
  });
});

Cypress.Commands.add('login', (email, senha = 'cypress12345') => {
  cy.visit('/login/');
  cy.get('input[name="email"]').clear();
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="senha"]').clear();
  cy.get('input[name="senha"]').type(senha);
  cy.contains('button', 'Entrar').first().click();
  cy.location('pathname', { timeout: 10000 }).should('not.eq', '/login/');
});

Cypress.Commands.add('criarConta', (nome, email, senha = 'cypress12345') => {
  cy.visit('/cadastro/');
  cy.get('input[name="nome"]').type(nome);
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="senha"]').type(senha);
  cy.get('input[name="confirmar_senha"]').type(senha);
  cy.step();
  cy.contains('button', 'Criar conta').click();
  cy.location('pathname', { timeout: 10000 }).should('include', '/inscricao/');
});

Cypress.Commands.add('preencherInscricao', (dados = {}) => {
  const valores = {
    nome: 'Nova Cypress',
    cpf: '11144477735',
    data_nascimento: '2001-02-03',
    telefone: '11911112222',
    disponibilidade: 'manha',
    observacoes: 'Inscricao criada pelo Cypress.',
    ...dados,
  };

  cy.get('input[name="nome"]').clear();
  cy.get('input[name="nome"]').type(valores.nome);
  cy.get('input[name="cpf"]').clear();
  cy.get('input[name="cpf"]').type(valores.cpf);
  cy.get('input[name="data_nascimento"]').clear();
  cy.get('input[name="data_nascimento"]').type(valores.data_nascimento);
  cy.get('input[name="telefone"]').clear();
  cy.get('input[name="telefone"]').type(valores.telefone);
  cy.get('select[name="disponibilidade"]').select(valores.disponibilidade);

  if (valores.observacoes) {
    cy.get('textarea[name="observacoes"]').clear();
    cy.get('textarea[name="observacoes"]').type(valores.observacoes);
  }

  cy.step();
});

Cypress.Commands.add('preencherContato', (dados = {}) => {
  const valores = {
    tipo: 'doacao',
    nome: 'Contato Cypress',
    email: `contato-${Date.now()}@example.com`,
    telefone: '11900000000',
    mensagem: 'Quero apoiar o projeto.',
    ...dados,
  };

  cy.get('select[name="tipo"]').select(valores.tipo);
  cy.get('input[name="nome"]').clear();
  cy.get('input[name="nome"]').type(valores.nome);
  cy.get('input[name="email"]').clear();
  cy.get('input[name="email"]').type(valores.email);
  cy.get('input[name="telefone"]').clear();
  cy.get('input[name="telefone"]').type(valores.telefone);
  cy.get('textarea[name="mensagem"]').clear();
  cy.get('textarea[name="mensagem"]').type(valores.mensagem);
  cy.step();
});

Cypress.Commands.add('anexarImagemBazar', (nome = 'item-cypress.png') => {
  cy.get('input[name="imagem"]').selectFile(
    {
      contents: Cypress.Buffer.from('imagem-cypress'),
      fileName: nome,
      mimeType: 'image/png',
    },
    { force: true }
  );
});
