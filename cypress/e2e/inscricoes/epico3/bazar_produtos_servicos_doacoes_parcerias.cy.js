describe('Epico 3 - Bazar, produtos, servicos, doacoes e parcerias', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  it('admin visualiza produtos e servicos cadastrados', () => {
    cy.login('cypress-admin@example.com');
    cy.visit('/inscricao/produtos/');
    cy.contains('Bolsa Cypress').should('be.visible');
    cy.contains('Bolsas').should('be.visible');
    cy.step();

    cy.visit('/inscricao/servicos/');
    cy.contains('Ajuste Cypress').should('be.visible');
    cy.contains('Costura').should('be.visible');
  });

  it('vitrine publica exibe, busca e filtra itens do bazar', () => {
    cy.visit('/bazar/');
    cy.contains('Cada peça é uma história.').should('be.visible');
    cy.contains('Bolsa Cypress').should('be.visible');
    cy.contains('Ajuste Cypress').should('be.visible');
    cy.step();

    cy.get('input[name="q"]').type('Bolsa Cypress');
    cy.get('form').first().submit();
    cy.contains('Bolsa Cypress').should('be.visible');
    cy.contains('Ajuste Cypress').should('not.exist');
  });

  it('usuario envia solicitacao de doacao', () => {
    cy.visit('/contato/?tipo=doacao');
    cy.get('select[name="tipo"]').should('have.value', 'doacao');
    cy.get('input[name="nome"]').type('Doadora Cypress');
    cy.get('input[name="email"]').type('doadora-cypress@example.com');
    cy.get('input[name="telefone"]').type('11900000000');
    cy.get('textarea[name="mensagem"]').type('Quero apoiar o projeto com uma doacao.');
    cy.step();

    cy.contains('button', 'Enviar solicitacao').click();
    cy.contains('Solicitacao enviada com sucesso').should('be.visible');
  });

  it('usuario envia solicitacao de parceria', () => {
    cy.visit('/contato/?tipo=parceria');
    cy.get('select[name="tipo"]').should('have.value', 'parceria');
    cy.get('input[name="nome"]').type('Parceira Cypress');
    cy.get('input[name="email"]').type('parceira-cypress@example.com');
    cy.get('input[name="telefone"]').type('11900000000');
    cy.get('textarea[name="mensagem"]').type('Quero propor uma parceria para o projeto.');
    cy.step();

    cy.contains('button', 'Enviar solicitacao').click();
    cy.contains('Solicitacao enviada com sucesso').should('be.visible');
  });

  it('admin visualiza contatos recebidos no Django Admin', () => {
    cy.login('cypress-admin@example.com');
    cy.visit('/django-admin/inscricoes/solicitacaocontato/');
    cy.contains('Contato Cypress').should('be.visible');
    cy.contains('contato-cypress@example.com').should('be.visible');
  });
});
