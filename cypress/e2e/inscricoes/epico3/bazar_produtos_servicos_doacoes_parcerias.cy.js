const sufixo = () => `${Date.now()}-${Cypress._.random(1000, 9999)}`;

const preencherProduto = (nome) => {
  cy.get('input[name="nome"]').type(nome);
  cy.get('textarea[name="descricao"]').type('Produto artesanal cadastrado pelo Cypress.');
  cy.get('input[name="preco"]').type('89.90');
  cy.get('input[name="categoria"]').type('Bolsas');
  cy.get('input[name="whatsapp_contato"]').type('5581988887777');
  cy.get('input[name="ativo"]').check();
  cy.anexarImagemBazar(`${nome}.png`);
  cy.step();
};

const preencherServico = (nome) => {
  cy.get('input[name="nome"]').type(nome);
  cy.get('textarea[name="descricao"]').type('Servico cadastrado pelo Cypress.');
  cy.get('input[name="tipo"]').type('Costura');
  cy.get('input[name="ativo"]').check();
  cy.anexarImagemBazar(`${nome}.png`);
  cy.step();
};

describe('Epico 3 - Bazar, produtos, servicos, doacoes e parcerias', () => {
  beforeEach(() => {
    cy.seedCypress();
  });

  describe('H1 - Cadastro de produtos e servicos', () => {
    it('H1 Cenario 1 - administrador acessa cadastro e registra item no bazar', () => {
      const nome = `Produto Geral Cypress ${sufixo()}`;

      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/produtos/novo/');
      cy.contains('Novo produto').should('be.visible');
      preencherProduto(nome);
      cy.contains('button', 'Salvar produto').click();

      cy.contains('Produto cadastrado com sucesso.').should('be.visible');
      cy.contains(nome).should('be.visible');
      cy.conclusao('administrador registra um item no bazar');
    });

    it('H1 Cenario 2 - salva produto com nome descricao preco e categoria', () => {
      const nome = `Bolsa Produto Cypress ${sufixo()}`;

      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/produtos/novo/');
      preencherProduto(nome);
      cy.contains('button', 'Salvar produto').click();

      cy.contains('Produto cadastrado com sucesso.').should('be.visible');
      cy.contains(nome).should('be.visible');
      cy.contains('Bolsas').should('be.visible');
      cy.conclusao('produto e salvo corretamente com seus dados principais');
    });

    it('H1 Cenario 3 - salva servico com descricao tipo e imagem', () => {
      const nome = `Ajuste Servico Cypress ${sufixo()}`;

      cy.login('cypress-admin@example.com');
      cy.visit('/inscricao/servicos/novo/');
      cy.contains('Novo servico').should('be.visible');
      preencherServico(nome);
      cy.contains('button', 'Salvar servico').click();

      cy.contains('Servico cadastrado com sucesso.').should('be.visible');
      cy.contains(nome).should('be.visible');
      cy.contains('Costura').should('be.visible');
      cy.conclusao('servico e salvo corretamente no bazar');
    });
  });

  describe('H2 - Vitrine de produtos e servicos', () => {
    it('H2 Cenario 1 - vitrine exibe itens em destaque', () => {
      cy.visit('/bazar/');

      cy.contains('Bolsa Cypress').should('be.visible');
      cy.contains('Ajuste Cypress').should('be.visible');
      cy.conclusao('vitrine publica exibe produtos e servicos ativos');
    });

    it('H2 Cenario 2 - filtros mostram apenas produtos correspondentes', () => {
      cy.visit('/bazar/');
      cy.get('input[name="q"]').type('Bolsa Cypress');
      cy.get('form').first().submit();

      cy.contains('Bolsa Cypress').should('be.visible');
      cy.contains('Ajuste Cypress').should('not.exist');
      cy.get('a[href*="tipo=produto"]').click();
      cy.contains('Bolsa Cypress').should('be.visible');
      cy.conclusao('busca e filtro restringem a vitrine ao produto correspondente');
    });

    it('H2 Cenario 3 - filtro sem resultados exibe mensagem informativa', () => {
      cy.visit('/bazar/?q=nada-cypress-inexistente');

      cy.contains('Nenhum item encontrado com os filtros selecionados.').should('be.visible');
      cy.contains('Ver todos os itens').should('be.visible');
      cy.conclusao('vitrine informa quando nenhum item atende aos filtros');
    });
  });

  describe('H3 - Gerenciamento de doacoes e parcerias', () => {
    it('H3 Cenario 1 - administrador visualiza lista de contatos recebidos', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/django-admin/inscricoes/solicitacaocontato/');

      cy.contains('Contato Cypress').should('be.visible');
      cy.contains('contato-cypress@example.com').should('be.visible');
      cy.conclusao('administrador visualiza solicitacoes recebidas no Django Admin');
    });

    it('H3 Cenario 2 - administrador visualiza detalhe do formulario enviado', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/django-admin/inscricoes/solicitacaocontato/');
      cy.contains('a', 'Contato Cypress').click();

      cy.get('input[name="nome"]').should('have.value', 'Contato Cypress');
      cy.get('input[name="email"]').should('have.value', 'contato-cypress@example.com');
      cy.get('textarea[name="mensagem"]').should('contain.value', 'Contato criado para teste Cypress.');
      cy.conclusao('detalhe administrativo exibe as informacoes enviadas no formulario');
    });

    it('H3 Cenario 3 - administrador atualiza status da solicitacao', () => {
      cy.login('cypress-admin@example.com');
      cy.visit('/django-admin/inscricoes/solicitacaocontato/');
      cy.contains('a', 'Contato Cypress').click();
      cy.get('select[name="status"]').select('em_analise');
      cy.step();
      cy.get('input[name="_save"]').click();

      cy.visit('/django-admin/inscricoes/solicitacaocontato/');
      cy.contains('a', 'Contato Cypress').click();
      cy.get('select[name="status"]').should('have.value', 'em_analise');
      cy.conclusao('status da solicitacao e atualizado corretamente');
    });
  });

  describe('H4 - Enviar solicitacao de doacao ou parceria', () => {
    it('H4 Cenario 1 - registra solicitacao com dados corretos', () => {
      const email = `solicitacao-${sufixo()}@example.com`;

      cy.visit('/contato/?tipo=parceria');
      cy.preencherContato({
        tipo: 'parceria',
        nome: 'Solicitante Cypress',
        email,
        mensagem: 'Quero propor uma parceria com dados validos.',
      });
      cy.contains('button', 'Enviar solicitacao').click();

      cy.contains('Solicitacao enviada com sucesso.').should('be.visible');
      cy.conclusao('solicitacao com dados validos e registrada com sucesso');
    });

    it('H4 Cenario 2 - exibe PIX e envia solicitacao de doacao', () => {
      const email = `doacao-${sufixo()}@example.com`;

      cy.visit('/contato/?tipo=doacao');

      cy.contains('Doacao via PIX').should('be.visible');
      cy.get('input[data-pix-value]').should('have.value', 'pix-cypress@entrelinhas.org');
      cy.contains('button', 'Copiar PIX').should('be.enabled').click();
      cy.contains('[data-pix-feedback]', /PIX copiado|Chave selecionada/).should('be.visible');
      cy.get('select[name="tipo"]').should('have.value', 'doacao');
      cy.preencherContato({
        tipo: 'doacao',
        nome: 'Doadora Cypress',
        email,
        mensagem: 'Quero fazer uma doacao para o projeto.',
      });
      cy.contains('button', 'Enviar solicitacao').click();

      cy.contains('Solicitacao enviada com sucesso.').should('be.visible');
      cy.conclusao('doacao exibe PIX da ONG e tambem registra a solicitacao para analise');
    });

    it('H4 Cenario 3 - envia solicitacao de parceria para analise', () => {
      const email = `parceria-${sufixo()}@example.com`;

      cy.visit('/contato/?tipo=parceria');
      cy.get('select[name="tipo"]').should('have.value', 'parceria');
      cy.preencherContato({
        tipo: 'parceria',
        nome: 'Parceira Cypress',
        email,
        mensagem: 'Quero propor uma parceria para o projeto.',
      });
      cy.contains('button', 'Enviar solicitacao').click();

      cy.contains('Solicitacao enviada com sucesso.').should('be.visible');
      cy.conclusao('solicitacao de parceria e enviada para analise');
    });
  });
});
