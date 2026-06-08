const dataISO = (dias) => {
  const data = new Date();
  data.setDate(data.getDate() + dias);
  return data.toISOString().slice(0, 10);
};

describe('Epico 2 - Aulas, presenca, certificados e area da aluna', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  describe('H1 - Registrar presenca', () => {
    it('H1 Cenario 1 - registra presenca de uma aluna', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/aulas/');
      cy.contains('tr', 'Aula Cypress').within(() => {
        cy.contains('a', 'Registrar presenca').click();
      });

      cy.contains('Aluna Cypress').should('be.visible');
      cy.get('input[type="checkbox"][name^="presente_"]').uncheck();
      cy.get('input[type="checkbox"][name^="presente_"]').check();
      cy.step();
      cy.contains('button', 'Salvar presencas').click();

      cy.contains('Presencas registradas com sucesso.').should('be.visible');
      cy.get('input[type="checkbox"][name^="presente_"]').should('be.checked');
      cy.conclusao('presenca da aluna foi registrada na aula');
    });

    it('H1 Cenario 2 - reabre aula e mostra status salvo', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/aulas/');
      cy.contains('tr', 'Aula Cypress').within(() => {
        cy.contains('a', 'Registrar presenca').click();
      });

      cy.contains('Aluna Cypress').should('be.visible');
      cy.get('input[type="checkbox"][name^="presente_"]').should('be.checked');
      cy.conclusao('status de presenca salvo aparece ao acessar novamente');
    });
  });

  describe('H2 - Gerenciar calendario de aulas', () => {
    it('H2 Cenario 1 - cadastra nova aula e exibe no calendario', () => {
      const dataAula = dataISO(14);
      const [ano, mes] = dataAula.split('-');

      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/aulas/nova/');
      cy.get('input[name="data"]').type(dataAula);
      cy.get('input[name="horario"]').type('10:30');
      cy.get('input[name="topico"]').type('Modelagem Cypress');
      cy.step();
      cy.contains('button', 'Criar aula').click();

      cy.contains('Aula criada com sucesso.').should('be.visible');
      cy.visit(`/inscricao/aulas/calendario/?ano=${ano}&mes=${Number(mes)}`);
      cy.contains('Modelagem Cypress').should('be.visible');
      cy.conclusao('aula cadastrada aparece no calendario administrativo');
    });

    it('H2 Cenario 2 - altera aula existente e atualiza calendario', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/aulas/');
      cy.contains('tr', 'Aula Cypress').within(() => {
        cy.contains('a', 'Editar').click();
      });

      cy.get('input[name="topico"]').clear();
      cy.get('input[name="topico"]').type('Aula Cypress Atualizada');
      cy.step();
      cy.contains('button', 'Salvar alteracoes').click();

      cy.contains('Aula atualizada com sucesso.').should('be.visible');
      cy.visit('/inscricao/aulas/calendario/');
      cy.contains('Aula Cypress Atualizada').should('be.visible');
      cy.conclusao('alteracao da aula e refletida no calendario');
    });

    it('H2 Cenario 3 - impede cadastro de aula com data invalida', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/aulas/nova/');
      cy.get('input[name="data"]').type(dataISO(-1));
      cy.get('input[name="horario"]').type('10:30');
      cy.get('input[name="topico"]').type('Aula Cypress Invalida');
      cy.step();
      cy.contains('button', 'Criar aula').click();

      cy.contains('Nao foi possivel criar a aula.').should('be.visible');
      cy.contains('A data da aula nao pode ser passada.').should('be.visible');
      cy.conclusao('data passada bloqueia o cadastro de aula');
    });
  });

  describe('H3 - Gerar certificado', () => {
    it('H3 Cenario 1 - certificado fica liberado para aluna concluida', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/certificados/');

      cy.contains('tr', 'Aluna Cypress').within(() => {
        cy.contains('Concluiu').should('be.visible');
        cy.contains('Baixar atual').should('be.visible');
      });
      cy.conclusao('certificado liberado aparece para aluna concluida');
    });

    it('H3 Cenario 2 - certificado nao aparece para aluna sem liberacao', () => {
      cy.login('cypress-sem-certificado@example.com');
      cy.visit('/inscricao/area-aluna/?aba=certificados');

      cy.contains('Status do certificado').should('be.visible');
      cy.contains('O certificado ficara disponivel apos a conclusao do curso.').should('be.visible');
      cy.contains('Baixar certificado').should('not.exist');
      cy.conclusao('aluna sem criterio concluido nao consegue baixar certificado');
    });
  });

  describe('H4 - Funcionalidade principal', () => {
    it('H4 Cenario 1 - usuaria matriculada acessa area da aluna', () => {
      cy.login('cypress-aluna@example.com');
      cy.visit('/inscricao/area-aluna/');

      cy.contains('Ola, Aluna Cypress').should('be.visible');
      cy.contains('Sua matricula no curso Costurando Sonhos esta aprovada.').should('be.visible');
      cy.conclusao('aluna aprovada visualiza a plataforma de acompanhamento');
    });

    it('H4 Cenario 2 - usuaria sem matricula ve bazar como area publica principal', () => {
      cy.login('cypress-sem-matricula@example.com');
      cy.visit('/bazar/');

      cy.contains('Bolsa Cypress').should('be.visible');
      cy.conclusao('usuaria sem matricula consegue acessar o bazar como funcionalidade principal');
    });

    it('H4 Cenario 3 - visitante nao logado acessa o bazar', () => {
      cy.visit('/bazar/');

      cy.contains('Bolsa Cypress').should('be.visible');
      cy.conclusao('visitante nao logado visualiza a vitrine publica do bazar');
    });

    it('H4 Cenario 4 - mudanca de status atualiza area exibida para usuaria', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/inscricoes/');
      cy.contains('tr', 'Edicao Cypress').within(() => {
        cy.get('select[name="status"]').select('aprovada');
      });
      cy.contains('Status da matricula atualizado com sucesso.').should('be.visible');
      cy.visit('/sair/');

      cy.login('cypress-edicao@example.com');
      cy.visit('/inscricao/area-aluna/');
      cy.contains('Ola, Edicao Cypress').should('be.visible');
      cy.contains('aprovada').should('be.visible');
      cy.conclusao('apos aprovacao a aluna passa a ver a area de acompanhamento');
    });
  });
});
