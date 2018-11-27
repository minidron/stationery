function toPriceString(value) {
    return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

function getOrderFromURL() {
    return new RegExp('/history/(\\d+)/').exec(window.location.href)[1];
}
