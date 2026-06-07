describe('Epico 2 - Aulas, presenca, certificados e area da aluna', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  it('admin visualiza calendario e registra presenca', () => {
    cy.login('cypress-admin@example.com');
    cy.visit('/inscricao/aulas/');
    cy.contains('Aula Cypress').should('be.visible');
    cy.contains('Calendario').click();
    cy.contains('Aula Cypress').should('be.visible');
    cy.step();

    cy.visit('/inscricao/aulas/');
    cy.contains('Registrar presenca').click();
    cy.contains('Aluna Cypress').should('be.visible');
    cy.get('input[type="checkbox"][name^="presente_"]').check();
    cy.contains('button', 'Salvar presencas').click();
    cy.contains('Presencas registradas com sucesso.').should('be.visible');
  });

  it('admin acessa certificados e ve certificado liberado', () => {
    cy.login('cypress-admin@example.com');
    cy.visit('/inscricao/certificados/');
    cy.contains('Aluna Cypress').should('be.visible');
    cy.contains('Concluiu').should('be.visible');
    cy.contains('Baixar atual').should('be.visible');
  });

  it('aluna acessa area principal e certificado', () => {
    cy.login('cypress-aluna@example.com');
    cy.visit('/inscricao/area-aluna/');
    cy.contains('Aluna Cypress').should('be.visible');
    cy.step();

    cy.contains('Certificados').click();
    cy.contains('Baixar certificado').should('be.visible');
  });
});
