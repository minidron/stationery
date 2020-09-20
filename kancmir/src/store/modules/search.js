import { UPDATE_CATEGORY_DATA, UPDATE_PRODUCT_DATA, UPDATE_QUERY } from '../mutation-types'
import { normalize, schema } from 'normalizr'

import axios from 'axios'
import { debounce } from 'lodash'

const state = () => ({
    categoryEntities: {},
    categoryList: [],
    productEntities: {},
    productList: [],
    query: ''
})

const getters = {
    categorySet (state) {
        return Object.keys(state.categoryEntities)
                     .map(id => state.categoryEntities[id])
    },
    productSet (state) {
        return Object.keys(state.productEntities)
                     .map(id => state.productEntities[id])
    }
}

const actions = {
    updateQuery ({ commit }, payload) {
        commit(UPDATE_QUERY, payload)
    },
    async _fetchHints ({ commit, state }, query) {
        // Если запрос меньше 3х символов, то возвращаем пустой объект.
        if (query.length < 3) {
            const normalizeData = { entities: {}, result: [] }

            commit(UPDATE_CATEGORY_DATA, normalizeData)
            commit(UPDATE_PRODUCT_DATA, normalizeData)
            return
        }

        const [categoryResponse, productResponse] = await Promise.all([
            axios.get('/api/search_category/', { params: { title: query } }),
            axios.get('/api/search_offer/', { params: { title: query } })
        ])

        // Есть вероятность, что вернётся старый запрос.
        if (query == state.query) {
            const category = new schema.Entity('categorySet'),
                  product = new schema.Entity('productSet'),
                  categoryData = normalize(categoryResponse.data, [category]),
                  productData = normalize(productResponse.data, [product])

            commit(UPDATE_CATEGORY_DATA, categoryData)
            commit(UPDATE_PRODUCT_DATA, productData)
        }
    },
    fetchHints: debounce(({ dispatch }, payload) => {
        dispatch('_fetchHints', payload)
    }, 200)
}

const mutations = {
    [UPDATE_CATEGORY_DATA] (state, data) {
        const { entities, result } = data
        state.categoryEntities = entities.categorySet || {}
        state.categoryList = result
    },
    [UPDATE_PRODUCT_DATA] (state, data) {
        const { entities, result } = data
        state.productEntities = entities.productSet || {}
        state.productList = result
    },
    [UPDATE_QUERY] (state, value) {
        state.query = value
    }
}

export default {
    actions,
    getters,
    mutations,
    namespaced: true,
    state
}
