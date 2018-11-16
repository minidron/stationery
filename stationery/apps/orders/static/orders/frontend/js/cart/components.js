/* Приложение для корзины в панели навигации.
============================================================================ */
Vue.component('cart-link', {
    props: {
        amount: String,
        href: String,
        initialAmount: String,
    },

    computed: {
        displayAmount: function () {
            let amount = this.initialAmount;

            if (this.amount) amount = this.amount;
            return amount;
        },
    },

    template: '<a class="navbar-cart--link" :href="href">{{ displayAmount }}</a>',
});
/* ------------------------------------------------------------------------- */


/* Приложение для товаров.
============================================================================ */
Vue.component('offer-price', {
    props: {
        offerId: String,
    },

    data: function () {
        return {
            quantity: '1',
        };
    },

    methods: {
        addOffer: function (e) {
            let vm = this;

            vm.$http({
                method: 'post',
                url: '/api/v2/orders/add_to_cart/',
                data: {
                    offer_id: vm.offerId,
                    quantity: vm.quantity,
                },
            })
                .then(function (response) {
                    if (response.data.hasOwnProperty('error')) {
                        vm.$emit('offer-limit-error');
                    }
                    else {
                        vm.$emit('offer-added');
                    }
                })
                .catch(function (error) {
                    console.log(error)
                });
        },
    },

    template: '\
        <div class="offer-price--cart">\
            <div class="offer-price--quantity">\
                <input class="quantity" type="text"\
                    :value="quantity"\
                    @input="quantity = $event.target.value"\
                >\
            </div>\
            <a href="" @click.prevent="addOffer" class="add-cart">В корзину</a>\
        </div>'
});


Vue.component('popup', {
    props: {
        text: {
            type: String,
            default: function () {
                return '';
            },
        },
    },

    data: function () {
        return {
            show: false,
        };
    },

    watch: {
        text: function () {
            let vm = this;

            if (vm.text != '') {
                vm.show = true;
                setTimeout(function () {
                    vm.$emit('close');
                }, 3000);
            }

            else {
                vm.show = false;
            }
        },
    },

    template: '<div class="offer-in-cart" v-if="show">{{ text }}</div>'
});
/* ------------------------------------------------------------------------- */
