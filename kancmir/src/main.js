import Search from './Search.vue'
import Vue from 'vue'
import { store } from './store'

Vue.config.productionTip = false

new Vue({
    store,
    render: h => h(Search),
}).$mount('#search_app')
