/* Настройки для AXIOS.
============================================================================ */
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
/* ------------------------------------------------------------------------- */


/* Регистрация дополнительных модулей.
============================================================================ */
Object.defineProperty(Vue.prototype, '$http', { value: axios });
Object.defineProperty(Vue.prototype, '$jQuery', { value: jQuery });
/* ------------------------------------------------------------------------- */
