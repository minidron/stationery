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
                url: '/api/v2/cart/add_to_cart/',
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
                    console.log(error);
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


/* Приложения для страницы корзины.
============================================================================ */
Vue.component('cart-offer', {
    props: {
        name: String,
        limit: String,
        offerId: String,
        article: String,
        title: String,
        link: String,
        initQuantity: String,
        price: String,
    },

    data: function () {
        return {
            quantity: this.initQuantity,
            show: true,
        };
    },

    computed: {
        formatedPrice: function () {
            return toPriceString(this.price.replace(',', '.'));
        },
        formatedTotalPrice: function () {
            return toPriceString(this.price.replace(',', '.') * this.quantity);
        },
    },

    methods: {
        updateItem: function (e) {
            let vm = this;

            vm.$http({
                method: 'post',
                url: '/api/v2/cart/update_cart/',
                data: {
                    offer_id: vm.offerId,
                    quantity: e.target.value,
                },
            })
                .then(function (response) {
                    if (response.data.hasOwnProperty('error')) {
                        e.target.value = vm.quantity;
                    }
                    else {
                        vm.quantity = e.target.value;
                    }
                })
                .catch(function (error) {
                    console.log(error);
                });
        },

        deleteItem: function (e) {
            let vm = this;

            vm.$http({
                method: 'post',
                url: '/api/v2/cart/remove_from_cart/',
                data: {
                    offer_id: vm.offerId,
                },
            })
                .then(function (response) {
                    vm.show = false;
                })
                .catch(function (error) {
                    console.log(error);
                });
        },
    },

    template: '\
        <div class="cart--item" v-if="show">\
            <div class="cart--item-offer">\
                <span class="article">{{ article }}</span>\
                <a class="cart--item-offer--link" :href="link">{{ title }}</a>\
            </div>\
            <div class="cart--item-quantity">\
                <div>{{ limit }}</div>\
                <input type="text" required="required"\
                    :name="name"\
                    :value="quantity"\
                    @input="updateItem"\
                >\
            </div>\
            <div class="cart--item-unit_price">x {{ formatedPrice }}</div>\
            <div class="cart--item-total_price">= {{ formatedTotalPrice }}</div>\
            <div class="cart--item-delete">\
                <a @click.prevent="deleteItem" class="cart--item-delete--link" href="#"></a>\
            </div>\
        </div>\
    '
});
/* ------------------------------------------------------------------------- */


/* Приложение для оплаты заказа.
============================================================================ */
Vue.component('delivery-address', {
    props: {
        value: String,
        initValue: String,
    },

    beforeMount: function () {
        let vm = this;

        if (vm.$parent.deliveryAddress == '') {
            vm.$parent.deliveryAddress = vm.initValue;
        }
    },

    mounted: function () {
        let vm = this;

        vm.$jQuery(vm.$el).autocomplete({
            serviceUrl: '/api/v2/addresses/suggest/',
            dataType: 'json',
            paramName: 'query',
            deferRequestBy: 1000,
            minChars: 2,

            transformResult: function (response) {
                return {
                    suggestions: vm.$jQuery.map(response, function (dataItem) {
                        return {
                            value: dataItem.address,
                            data: dataItem.zip_code,
                        };
                    }),
                };
            },

            onSelect: function (response) {
                vm.$emit('select', response.data);
            },
        });
    },

    destroyed: function () {
        let vm = this;

        vm.$jQuery(vm.$el).autocomplete('dispose');
    },

    template: '<input :value="value" @input="$emit(\'input\', $event.target.value)">',
});


Vue.component('delivery-type', {
    props: {
        id: String,
        name: String,
        required: String,
        value: String,
        initValue: String,
        choices: Array,
    },

    beforeMount: function () {
        let vm = this;

        if (vm.$parent.deliveryType == '') {
            vm.$parent.deliveryType = vm.initValue;
        }
    },

    template: '\
        <ul :id="id">\
            <li v-for="(choice, index) in choices">\
                <label :for="id + \'_\' + index">\
                    <input type="radio" :name="name" :value="choice.value"\
                        :id="id + \'_\' + index"\
                        :checked="choice.value == value"\
                        :required="required"\
                        @input="$emit(\'input\', $event.target.value)">\
                    {{ choice.label }}\
                </label>\
            </li>\
        </ul>\
    ',
});


Vue.component('delivery-zip', {
    props: {
        value: String,
        initValue: String,
    },

    beforeMount: function () {
        let vm = this;

        if (vm.$parent.zipCode == '') {
            vm.$parent.zipCode = vm.initValue;
        }
    },

    template: '<input :value="value" @input="$emit(\'input\', $event.target.value)">',
});


Vue.component('delivery-price', {
    props: {
        value: Number,
    },

    computed: {
        formatedValue: function () {
            return toPriceString(this.value);
        },
    },

    template: '<strong>{{ formatedValue }} руб.</strong>',
});
/* ------------------------------------------------------------------------- */
