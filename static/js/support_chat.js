(function () {
    const sugestoes = {
        public: [
            'Como faco minha inscricao?',
            'Os cursos sao gratuitos?',
            'Como funciona o bazar?',
            'Como posso apoiar a ONG?',
        ],
        student: [
            'Como vejo minha frequencia?',
            'Onde vejo minhas proximas aulas?',
            'Quando meu certificado fica disponivel?',
            'Como altero meus dados?',
        ],
    };

    const saudacoes = {
        public: 'Ol\u00e1! Sou a **Lia**, assistente da EntreLinhas. \ud83d\udc9c\n\nPosso te ajudar com d\u00favidas sobre **cursos**, **inscri\u00e7\u00f5es** ou o **bazar solid\u00e1rio**. Como posso te ajudar hoje?',
        student: 'Ol\u00e1! Sou a **Lia**, assistente da EntreLinhas. \ud83d\udc9c\n\nPosso te ajudar com d\u00favidas sobre **cursos**, **inscri\u00e7\u00f5es**, **frequ\u00eancia**, **certificados** ou o **bazar solid\u00e1rio**. Como posso te ajudar hoje?',
    };

    function escaparHtml(texto) {
        return texto
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function textoNormalizado(texto) {
        return texto
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    function precisaMostrarSuporte(texto) {
        const normalizado = textoNormalizado(texto);

        return (
            normalizado.includes('formulario de suporte')
            || normalizado.includes('abrir suporte')
            || normalizado.includes('falar com suporte')
            || normalizado.includes('equipe de suporte')
            || normalizado.includes('atendimento humano')
            || normalizado.includes('abrir chamado')
            || normalizado.includes('nao resolveu')
            || normalizado.includes('nao consegui')
            || normalizado.includes('nao consigo')
        );
    }

    function renderizarMarkdownSeguro(texto, supportUrl, permitirSuporte) {
        let html = escaparHtml(texto)
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        if (permitirSuporte && supportUrl && precisaMostrarSuporte(texto)) {
            html = html.replace(
                /formul(?:a|&aacute;|\u00e1)rio de suporte/gi,
                `<a href="${supportUrl}" class="support-chat__message-link">formul\u00e1rio de suporte</a>`
            );
            html += `<br><a href="${supportUrl}" class="support-chat__support-button">Abrir formul\u00e1rio de suporte</a>`;
        }

        return html;
    }

    function csrfToken(chat) {
        const tokenInput = chat.querySelector('input[name="csrfmiddlewaretoken"]');

        if (tokenInput && tokenInput.value) {
            return tokenInput.value;
        }

        const cookies = document.cookie ? document.cookie.split(';') : [];

        for (const cookie of cookies) {
            const [nome, ...valor] = cookie.trim().split('=');

            if (nome === 'csrftoken') {
                return decodeURIComponent(valor.join('='));
            }
        }

        return '';
    }

    function carregarMensagens(chave, contexto) {
        try {
            const salvas = JSON.parse(sessionStorage.getItem(chave) || '[]');

            if (Array.isArray(salvas) && salvas.length) {
                return salvas;
            }
        } catch (erro) {
            sessionStorage.removeItem(chave);
        }

        return [
            {
                role: 'assistant',
                content: saudacoes[contexto] || saudacoes.public,
            },
        ];
    }

    function salvarMensagens(chave, mensagens) {
        sessionStorage.setItem(chave, JSON.stringify(mensagens.slice(-20)));
    }

    function iniciarChat(chat) {
        const contexto = chat.dataset.chatContext === 'student' ? 'student' : 'public';
        const chaveHistorico = `lia-chat-${contexto}`;
        const url = chat.dataset.chatUrl;
        const supportUrl = chat.dataset.supportUrl;
        const toggle = chat.querySelector('[data-chat-toggle]');
        const iconOpen = chat.querySelector('[data-chat-icon-open]');
        const iconClose = chat.querySelector('[data-chat-icon-close]');
        const panel = chat.querySelector('[data-chat-panel]');
        const messagesEl = chat.querySelector('[data-chat-messages]');
        const suggestionsEl = chat.querySelector('[data-chat-suggestions]');
        const errorEl = chat.querySelector('[data-chat-error]');
        const form = chat.querySelector('[data-chat-form]');
        const input = chat.querySelector('[data-chat-input]');
        const send = chat.querySelector('[data-chat-send]');
        let mensagens = carregarMensagens(chaveHistorico, contexto);
        let enviando = false;

        function rolarFim() {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function renderizarMensagens() {
            messagesEl.innerHTML = '';

            mensagens.forEach((mensagem) => {
                const linha = document.createElement('div');
                linha.className = `support-chat__message support-chat__message--${mensagem.role}`;

                const bolha = document.createElement('p');
                bolha.innerHTML = renderizarMarkdownSeguro(
                    mensagem.content,
                    supportUrl,
                    mensagem.role === 'assistant'
                );
                linha.appendChild(bolha);
                messagesEl.appendChild(linha);
            });

            rolarFim();
        }

        function renderizarSugestoes() {
            suggestionsEl.innerHTML = '';

            if (mensagens.length > 1) {
                suggestionsEl.hidden = true;
                return;
            }

            suggestionsEl.hidden = false;

            (sugestoes[contexto] || sugestoes.public).forEach((texto) => {
                const botao = document.createElement('button');
                botao.type = 'button';
                botao.textContent = texto;
                botao.addEventListener('click', () => enviarMensagem(texto));
                suggestionsEl.appendChild(botao);
            });
        }

        function definirAberto(aberto) {
            panel.hidden = !aberto;
            iconOpen.hidden = aberto;
            iconClose.hidden = !aberto;
            toggle.setAttribute('aria-expanded', aberto ? 'true' : 'false');
            toggle.setAttribute('aria-label', aberto ? 'Fechar chat de suporte' : 'Abrir chat de suporte');

            if (aberto) {
                setTimeout(() => input.focus(), 60);
                rolarFim();
            }
        }

        function mostrarErro(texto, mostrarSuporte) {
            const textoSeguro = escaparHtml(texto);

            if (mostrarSuporte && supportUrl) {
                errorEl.innerHTML = `${textoSeguro}<br><a href="${supportUrl}" class="support-chat__support-button">Abrir formul\u00e1rio de suporte</a>`;
            } else {
                errorEl.textContent = texto;
            }

            errorEl.hidden = false;
        }

        function limparErro() {
            errorEl.textContent = '';
            errorEl.innerHTML = '';
            errorEl.hidden = true;
        }

        function definirCarregando(ativo) {
            enviando = ativo;
            input.disabled = ativo;
            send.disabled = ativo;

            if (ativo) {
                mensagens.push({
                    role: 'assistant',
                    content: 'Lia esta digitando...',
                    typing: true,
                });
            } else {
                mensagens = mensagens.filter((mensagem) => !mensagem.typing);
            }

            renderizarMensagens();
        }

        async function enviarMensagem(textoManual) {
            const texto = (textoManual || input.value).trim();

            if (!texto || enviando) {
                return;
            }

            const usuarioPediuSuporte = precisaMostrarSuporte(texto);
            limparErro();
            input.value = '';
            input.style.height = '';
            mensagens.push({role: 'user', content: texto});
            salvarMensagens(chaveHistorico, mensagens);
            renderizarMensagens();
            renderizarSugestoes();
            definirCarregando(true);

            try {
                const resposta = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken(chat),
                    },
                    body: JSON.stringify({
                        context: contexto,
                        messages: mensagens.filter((mensagem) => !mensagem.typing),
                    }),
                });
                const dados = await resposta.json();
                definirCarregando(false);

                if (!resposta.ok || dados.error) {
                    mostrarErro(dados.error || 'Nao consegui responder agora.', true);
                    return;
                }

                let respostaLia = dados.reply || 'Nao consegui montar uma resposta agora.';

                if (usuarioPediuSuporte && !precisaMostrarSuporte(respostaLia)) {
                    respostaLia += '\n\nSe preferir, abra o formul\u00e1rio de suporte.';
                }

                mensagens.push({
                    role: 'assistant',
                    content: respostaLia,
                });
                salvarMensagens(chaveHistorico, mensagens);
                renderizarMensagens();
            } catch (erro) {
                definirCarregando(false);
                mostrarErro('Nao consegui conectar com a Lia agora. Tente novamente em instantes.', true);
            }
        }

        toggle.addEventListener('click', () => definirAberto(panel.hidden));

        form.addEventListener('submit', (evento) => {
            evento.preventDefault();
            enviarMensagem();
        });

        input.addEventListener('keydown', (evento) => {
            if (evento.key === 'Enter' && !evento.shiftKey) {
                evento.preventDefault();
                enviarMensagem();
            }
        });

        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
        });

        document.addEventListener('keydown', (evento) => {
            if (evento.key === 'Escape' && !panel.hidden) {
                definirAberto(false);
            }
        });

        renderizarMensagens();
        renderizarSugestoes();
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-support-chat]').forEach(iniciarChat);
    });
}());
