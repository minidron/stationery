(function(window, document) {
    function openModal(modal) {
        modal.classList.add('open');
    }

    function closeModal(modal) {
        modal.classList.remove('open');
    }

    document.addEventListener('DOMContentLoaded', function () {
        const modalWindow = document.querySelector('.modal-window');
        const showModal = JSON.parse(Cookies.get('showModal') || true)
        const closeBtn = document.querySelector('.modal-close');
        const selectBtn = document.querySelectorAll('.modal-select');

        if (!window.isAuth && showModal) {
            openModal(modalWindow);
        }

        closeBtn.addEventListener('click', function () {
            closeModal(modalWindow);
        });

        selectBtn.forEach(function (el) {
            el.addEventListener('click', function () {
                Cookies.set('showModal', false);
                closeModal(modalWindow);
            });
        });
    });
})(window, document);
