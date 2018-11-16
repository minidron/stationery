/* Приложение для корзины в панели навигации.
============================================================================ */
window.navbarCart = new Vue({
    delimiters: ['[[', ']]'],
    el: '#navbar-cart-app',

    data: {
        amount: '',
    },

    methods: {
        fetchCart: function (e) {
            let vm = this;

            vm.$http.get('/api/v2/orders/cart/')
                .then(function (response) {
                    vm.amount = toPriceString(response.data.amount);
                })
                .catch(function (error) {
                    console.log(error)
                });
        },
    },
});
/* ------------------------------------------------------------------------- */


/* Приложение для товаров.
============================================================================ */
window.offersCart = new Vue({
    delimiters: ['[[', ']]'],
    el: '#offers-cart-app',

    data: {
        popupText: '',
    },

    methods: {
        updateNavbarCart: function (e) {
            this.popupText = 'Товар добавлен в корзину';
            navbarCart.fetchCart();
        },
        showLimitError: function (e) {
            this.popupText = 'Недостаточно товара в наличии';
        },
    },
});
/* ------------------------------------------------------------------------- */
