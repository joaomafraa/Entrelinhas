const emailUnico = (prefixo) => `${prefixo}-${Date.now()}-${Cypress._.random(1000, 9999)}@example.com`;

describe('Epico 1 - Inscricao, gerenciamento e matricula', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  describe('H1 - Inscricao no curso', () => {
    it('H1 Cenario 1 - registra inscricao com dados validos', () => {
      const email = emailUnico('cypress-inscricao-valida');

      cy.criarConta('Nova Cypress', email);
      cy.preencherInscricao({ nome: 'Nova Cypress' });
      cy.contains('button', 'Enviar').click();
      cy.step();

      cy.location('pathname').should('include', '/inscricao/sucesso/');
      cy.contains('Nova Cypress').should('be.visible');
      cy.conclusao('a inscricao foi registrada com sucesso');
    });

    it('H1 Cenario 2 - exibe erros para campos obrigatorios vazios', () => {
      const email = emailUnico('cypress-inscricao-vazia');

      cy.criarConta('Obrigatorios Cypress', email);
      cy.get('input[name="nome"]').clear();
      cy.step();
      cy.contains('button', 'Enviar').click();

      cy.location('pathname').should('include', '/inscricao/');
      cy.get('input[name="nome"]:invalid').should('exist');
      cy.get('input[name="cpf"]:invalid').should('exist');
      cy.conclusao('campos obrigatorios vazios impedem a conclusao da inscricao');
    });

    it('H1 Cenario 3 - rejeita letras em CPF ou telefone', () => {
      const email = emailUnico('cypress-inscricao-invalida');

      cy.criarConta('Numeros Cypress', email);
      cy.preencherInscricao({
        nome: 'Numeros Cypress',
        cpf: 'abc',
        telefone: 'telefone',
      });
      cy.contains('button', 'Enviar').click();

      cy.contains('Informe um CPF').should('be.visible');
      cy.contains('O telefone deve conter apenas numeros.').should('be.visible');
      cy.location('pathname').should('include', '/inscricao/');
      cy.conclusao('CPF e telefone com letras exibem mensagens informativas e nao concluem a inscricao');
    });
  });

  describe('H2 - Gerenciar inscricoes', () => {
    it('H2 Cenario 1 - administrador visualiza inscricoes registradas', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/inscricoes/');

      cy.contains('Aluna Cypress').should('be.visible');
      cy.contains('Costurando Sonhos').should('be.visible');
      cy.contains('529.982.247-25').should('be.visible');
      cy.conclusao('administrador visualiza os dados das alunas cadastradas');
    });

    it('H2 Cenario 2 - administrador ve mensagem quando nao ha inscricoes', () => {
      cy.login('cypress-admin@example.com');
      cy.exec('python manage.py shell -c "from inscricoes.models import Inscricao; Inscricao.objects.all().delete()"', {
        env: {
          SECRET_KEY: 'django-insecure-cypress-test-key',
          DEBUG: 'True',
        },
      });
      cy.visit('/inscricao/inscricoes/');

      cy.contains('Nenhuma inscricao encontrada.').should('be.visible');
      cy.contains('Mostrando 0-0 de 0').should('be.visible');
      cy.conclusao('lista vazia apresenta mensagem informativa para o administrador');
    });

    it('H2 Cenario 3 - administrador visualiza detalhes da inscricao', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/inscricoes/');
      cy.contains('tr', 'Aluna Cypress').within(() => {
        cy.contains('a', 'Ver').click();
      });

      cy.contains('Aluna Cypress').should('be.visible');
      cy.contains('cypress-aluna@example.com').should('be.visible');
      cy.contains('Costurando Sonhos').should('be.visible');
      cy.conclusao('detalhe exibe nome, email e informacoes do curso');
    });
  });

  describe('H3 - Gerenciar matricula', () => {
    it('H3 Cenario 1 - aluna atualiza dados da propria matricula', () => {
      cy.login('cypress-edicao@example.com');
      cy.visit('/inscricao/inscricoes/');
      cy.contains('tr', 'Edicao Cypress').within(() => {
        cy.contains('a', 'Editar').click();
      });

      cy.get('input[name="telefone"]').clear();
      cy.get('input[name="telefone"]').type('11988887777');
      cy.get('textarea[name="observacoes"]').clear();
      cy.get('textarea[name="observacoes"]').type('Atualizacao feita pelo Cypress.');
      cy.step();
      cy.contains('button', 'Salvar').click();

      cy.contains('Matricula atualizada com sucesso.').should('be.visible');
      cy.contains('Edicao Cypress').should('be.visible');
      cy.conclusao('aluna atualiza a propria matricula com dados validos');
    });

    it('H3 Cenario 2 - aluna cancela a propria matricula', () => {
      cy.login('cypress-edicao@example.com');
      cy.visit('/inscricao/inscricoes/');
      cy.contains('tr', 'Edicao Cypress').within(() => {
        cy.contains('a', 'Cancelar').click();
      });

      cy.contains('button', 'Sim, cancelar').click();
      cy.contains('cancelada').should('be.visible');
      cy.contains('Voce ainda nao possui inscricoes').should('be.visible');
      cy.conclusao('matricula cancelada deixa de aparecer para a aluna');
    });

    it('H3 Cenario 3 - edicao com dados invalidos exibe erro', () => {
      cy.login('cypress-edicao@example.com');
      cy.visit('/inscricao/inscricoes/');
      cy.contains('tr', 'Edicao Cypress').within(() => {
        cy.contains('a', 'Editar').click();
      });

      cy.get('input[name="telefone"]').clear();
      cy.get('input[name="telefone"]').type('abc');
      cy.step();
      cy.contains('button', 'Salvar').click();

      cy.contains('Nao foi possivel salvar as alteracoes.').should('be.visible');
      cy.contains('O telefone deve conter apenas numeros.').should('be.visible');
      cy.conclusao('dados invalidos na edicao mantem a aluna no formulario com erro visivel');
    });
  });
});
