Cypress.Commands.add('step', () => {
  if (!Cypress.env('screencast')) {
    return;
  }

  const delay = Number(Cypress.env('stepDelay') || 1500);

  cy.wait(delay);
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
