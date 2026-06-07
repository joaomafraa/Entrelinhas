describe('Epico 1 - Inscricao, gerenciamento e matricula', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  it('permite criar conta e enviar inscricao no curso', () => {
    cy.visit('/cadastro/');
    cy.get('input[name="nome"]').type('Nova Cypress');
    cy.get('input[name="email"]').type('cypress-nova@example.com');
    cy.get('input[name="senha"]').type('cypress12345');
    cy.get('input[name="confirmar_senha"]').type('cypress12345');
    cy.contains('button', 'Criar conta').click();
    cy.step();

    cy.url().should('include', '/inscricao/');
    cy.get('input[name="nome"]').clear().type('Nova Cypress');
    cy.get('input[name="cpf"]').type('11144477735');
    cy.get('input[name="data_nascimento"]').type('2001-02-03');
    cy.get('input[name="telefone"]').type('11911112222');
    cy.get('select[name="disponibilidade"]').select('manha');
    cy.get('textarea[name="observacoes"]').type('Inscricao criada pelo Cypress.');
    cy.contains('button', 'Enviar').click();
    cy.step();

    cy.url().should('include', '/sucesso/');
    cy.contains('Nova Cypress').should('be.visible');
  });

  it('admin visualiza lista e detalhe de inscricao', () => {
    cy.login('cypress-admin@example.com');
    cy.visit('/inscricao/inscricoes/');
    cy.contains('Aluna Cypress').should('be.visible');
    cy.contains('Costurando Sonhos').should('be.visible');
    cy.step();

    cy.contains('Ver').click();
    cy.contains('Aluna Cypress').should('be.visible');
    cy.contains('cypress-aluna@example.com').should('be.visible');
  });

  it('aluna edita a propria matricula', () => {
    cy.login('cypress-aluna@example.com');
    cy.visit('/inscricao/inscricoes/');
    cy.contains('Editar').click();
    cy.get('input[name="telefone"]').clear().type('11988887777');
    cy.get('textarea[name="observacoes"]').clear().type('Atualizacao feita pelo Cypress.');
    cy.contains('button', 'Salvar').click();
    cy.step();

    cy.contains('Aluna Cypress').should('be.visible');
  });
});
