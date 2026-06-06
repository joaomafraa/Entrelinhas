(() => {
    const modalElement = document.getElementById('adminConfirmDeleteModal');

    if (!modalElement || typeof bootstrap === 'undefined') {
        return;
    }

    const modal = new bootstrap.Modal(modalElement);
    const title = modalElement.querySelector('#adminConfirmDeleteTitle');
    const text = modalElement.querySelector('#adminConfirmDeleteText');
    const submitButton = modalElement.querySelector('[data-confirm-delete-submit]');
    let pendingForm = null;

    document.addEventListener('submit', (event) => {
        const form = event.target.closest('form[data-confirm-delete]');

        if (!form) {
            return;
        }

        event.preventDefault();

        pendingForm = form;
        title.textContent = form.dataset.confirmTitle || 'Confirmar exclusao';
        text.textContent = form.dataset.confirmText || 'Esta acao nao podera ser desfeita.';
        submitButton.textContent = form.dataset.confirmButton || 'Excluir';
        modal.show();
    });

    submitButton.addEventListener('click', () => {
        if (!pendingForm) {
            return;
        }

        modal.hide();
        pendingForm.submit();
        pendingForm = null;
    });

    modalElement.addEventListener('hidden.bs.modal', () => {
        pendingForm = null;
    });
})();
