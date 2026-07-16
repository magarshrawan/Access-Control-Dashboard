// ── Vertex Access Control — main.js ──────────────────────────

// Auto-dismiss alerts after 4 seconds with fade out
document.querySelectorAll('.alert').forEach(function (el) {
    setTimeout(function () {
        el.style.transition = 'opacity 0.4s, transform 0.4s';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(function () { el.remove(); }, 400);
    }, 4000);
});

// ── Confirmation modal ────────────────────────────────────────
// Usage: add data-confirm="Your message here" to any form or button
// and data-confirm-title="Title" (optional)

function createModal() {
    if (document.getElementById('confirm-modal')) return;
    const modal = document.createElement('div');
    modal.id = 'confirm-modal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-box">
            <div class="modal-icon">⚠️</div>
            <p class="modal-title" id="modal-title">Are you sure?</p>
            <p class="modal-message" id="modal-message">This action cannot be undone.</p>
            <div class="modal-actions">
                <button class="btn-secondary" id="modal-cancel">Cancel</button>
                <button class="btn-danger"    id="modal-confirm">Confirm</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('modal-cancel').addEventListener('click', function () {
        modal.classList.remove('active');
    });
    modal.addEventListener('click', function (e) {
        if (e.target === modal) modal.classList.remove('active');
    });
}

function showModal(title, message, onConfirm) {
    createModal();
    document.getElementById('modal-title').textContent   = title;
    document.getElementById('modal-message').textContent = message;
    const modal   = document.getElementById('confirm-modal');
    const confirm = document.getElementById('modal-confirm');
    modal.classList.add('active');

    // Remove old listener and add new one
    const newConfirm = confirm.cloneNode(true);
    confirm.parentNode.replaceChild(newConfirm, confirm);
    newConfirm.addEventListener('click', function () {
        modal.classList.remove('active');
        onConfirm();
    });
}

// Intercept all forms with data-confirm attribute
document.addEventListener('submit', function (e) {
    const form = e.target;
    const message = form.dataset.confirm;
    if (!message) return;

    e.preventDefault();
    const title = form.dataset.confirmTitle || 'Are you sure?';
    showModal(title, message, function () {
        form.removeAttribute('data-confirm');
        form.submit();
    });
});

// Intercept buttons/links with data-confirm attribute
document.addEventListener('click', function (e) {
    const el = e.target.closest('[data-confirm]');
    if (!el || el.tagName === 'FORM') return;
    e.preventDefault();
    const message = el.dataset.confirm;
    const title   = el.dataset.confirmTitle || 'Are you sure?';
    showModal(title, message, function () {
        if (el.tagName === 'A') {
            window.location.href = el.href;
        } else if (el.closest('form')) {
            el.closest('form').submit();
        }
    });
});
