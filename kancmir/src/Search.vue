<template>
    <div :class="['header-search', {focus: isFocus}]"
        @mouseover="isBlockHover=true"
        @mouseout="isBlockHover=false">

        <input type="text"
            :value="query"
            @input="updateQuery($event.target.value)"
            @focus="isInputisFocus=true"
            @blur="isInputisFocus=false"
            @keyup.enter="search(query)"
            @keyup.esc="updateQuery('')"
            id="header-search"
            placeholder="Введите код или название товара..."
            autocomplete="off">

        <div class="header-search--button"
            @click="search(query)"></div>

        <div class="autocomplete-suggestions">
            <div class="autocomplete-suggestion"
                v-for="product in productSet"
                :key="product.id"
                @click="openLink(product.url)">

                <div class="suggestion">
                    <span :inner-html.prop="product.title | selectMatch(query)"></span>
                    <div class="category">{{ product.category }}</div>
                </div>
                <div class="price">{{ product.price_retail }}</div>
            </div>

            <div class="autocomplete-suggestion suggestion-category"
                v-for="category in categorySet"
                :key="category.id"
                @click="openLink(category.url)">

                <div class="suggestion">
                    <div class="category"
                        :inner-html.prop="category.title | selectMatch(query)" />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import { SEARCH_MODULE } from './const'
import { escapeRegExChars } from './utils'
import searchModule from './store/modules/search'
import { store } from './store'

// Регистрация search модуля.
if (!store.state[SEARCH_MODULE]) store.registerModule(SEARCH_MODULE, searchModule)

export default {
    name: 'Search',
    filters: {
        selectMatch: function (value, query) {
            return value.replace(
                new RegExp(`(${escapeRegExChars(query)})`, 'gi'),
                '<strong>$1</strong>')
        }
    },
    data () {
        return {
            isBlockHover: false,
            isInputisFocus: false
        }
    },
    computed: {
        isFocus () {
            return this.isBlockHover | this.isInputisFocus
        },
        ...mapGetters(SEARCH_MODULE, ['categorySet', 'productSet']),
        ...mapState(SEARCH_MODULE, ['query'])
    },
    watch: {
        query (value) {
            this.fetchHints(value)
        }
    },
    methods: {
        openLink (path) {
            window.location.href = path
        },
        search (query) {
            if (query.length > 0) window.location.href = `/search/?q=${query}`
        },
        ...mapActions(SEARCH_MODULE, ['fetchHints', 'updateQuery'])
    }
}
</script>
