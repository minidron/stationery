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
