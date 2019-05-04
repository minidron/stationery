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

            vm.$http.get('/api/v2/cart/cart/')
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
        deliveryType: '',
        deliveryAddress: '',
        zipCode: '',
        popupText: '',
        deliveryPrice: 0,
    },

    computed: {
        delivery: function () {
            return this.deliveryType, this.zipCode, Date.now();
        },
    },

    watch: {
        delivery: function () {
            let vm = this;

            if (vm.deliveryType == '1') {
                vm.deliveryPrice = 0;
            }

            else {
                if (vm.zipCode.length == 6) {
                    vm.$http({
                        method: 'post',
                        url: '/api/v2/orders/delivery_price/',
                        data: {
                            delivery_type: vm.deliveryType,
                            zip_code: vm.zipCode,
                            order_id: getOrderFromURL(),
                        },
                    })
                        .then(function (response) {
                            vm.deliveryPrice = response.data.price;
                        })
                        .catch(function (error) {
                            console.log(error)
                        });
                }
            }
        },

        deliveryPrice: function (newPrice, oldPrice) {
            if (newPrice != oldPrice) {
                let vm = this,
                    priceEl = vm.$jQuery('[data-delivery-price]'),
                    price = priceEl.data('deliveryPrice')
                    fullPrice = newPrice + parseFloat(price);

                priceEl.text(toPriceString(fullPrice) + ' руб.');
            }
        },
    },

    methods: {
        updateNavbarCart: function (e) {
            this.popupText = 'Товар добавлен в корзину';
            navbarCart.fetchCart();
        },

        showLimitError: function (e) {
            this.popupText = 'Недостаточно товара в наличии';
        },

        setZipCode: function (value) {
            this.zipCode = value;
        },
    },
});
/* ------------------------------------------------------------------------- */
