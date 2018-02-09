do ($=jQuery, window, document) ->

  toPrice = (value) ->
    price = value.toFixed(2).replace /\B(?=(\d{3})+(?!\d))/g, ' '


  # Псевдо hover на поисковый блок
  # ---------------------------------------------------------------------------
  $ ->
    searchBlock = $ '.header-search'
    searchInput = $ '#header-search'

    searchBlock.hover(
      ->
        searchBlock.addClass 'focus'
      ->
        if not searchInput.is ':focus'
          searchBlock.removeClass 'focus'
    )

    searchBlock.click (e) ->
      if e.target == this
        searchInput.focus()

    searchInput.focus ->
      searchBlock.addClass 'focus'

    searchInput.focusout ->
      if not searchBlock.is ':hover'
        searchBlock.removeClass 'focus'
  # ---------------------------------------------------------------------------


  # ДОБАВЛЕНИЕ В КОРЗИНУ
  # ---------------------------------------------------------------------------
  $ ->
    cart = $ '#cart-full-price'

    $('a[data-offer-id]').click (e) ->
      e.preventDefault()

      el = $ @
      quantity = el.closest('.offer-price--cart').find('.quantity').val()

      $.ajax
        type: 'POST'
        url: '/api/orders/'
        data: {
          'offer': $(this).data('offerId')
          'quantity': quantity
          'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        }
        success: (data, status) =>
          cart.text toPrice data.amount
          console.log status
        error: (data, status) =>
          console.log status
  # ---------------------------------------------------------------------------


  # КОРЗИНА ТОВАРОВ
  # ---------------------------------------------------------------------------
  $ ->
    $('.cart--item-quantity input').on 'keyup change', (e) ->
      el = $ @
      txt = el.closest('.cart--item').find('.cart--item-unit_price').text()
      price = parseFloat txt.replace /[^\d\.]+/g, ''
      totalPrice = el.val() * price
      el.closest('.cart--item').find('.cart--item-total_price').text "= #{toPrice(totalPrice)}"
      $('.cart-info--price').trigger 'htmlchange'

    $('.cart-info--price').on 'htmlchange', (e) ->
      el = $ @
      sum = 0
      $.each $('.cart--item-total_price'), ->
        sum += parseFloat $(this).text().replace /[^\d\.]+/g, ''
      el.text "= #{toPrice(sum)}"
  # ---------------------------------------------------------------------------


  # AUTOCOMLETE
  # ---------------------------------------------------------------------------
  $ ->
    searchBlock = $ '.header-search'

    escapeRegExChars = (value) ->
      value.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&")

    $('#header-search').devbridgeAutocomplete
      serviceUrl: '/api/search_offer/'
      paramName: 'title'
      minChars: 2
      maxHeight: 'auto'
      appendTo: searchBlock
      transformResult: (response) ->
        suggestions: $.map JSON.parse(response), (dataItem) ->
          value: dataItem.title, data:
            link: dataItem.url
            price: dataItem.price_retail
      formatResult: (suggestion, currentValue) ->
        if not currentValue
          return suggestion.value

        pattern = '(' + escapeRegExChars(currentValue) + ')'
        result = '<div class="suggestion">' + suggestion.value + '</div><div class="price">' + suggestion.data.price + '</div>'
        result.replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>')

      onSelect: (suggestion) ->
          window.location.href = suggestion.data.link
  # ---------------------------------------------------------------------------


  # PRICE SLIDER
  # ---------------------------------------------------------------------------
  $ ->
    handlesSlider = document.getElementById('offer-filter--price-slider')
    if not handlesSlider
      return

    minPrice = document.getElementById('offer-filter--price-min')
    maxPrice = document.getElementById('offer-filter--price-max')

    noUiSlider.create handlesSlider,
      connect: true
      start: [
        parseInt(minPrice.value)
        parseInt(maxPrice.value)]
      range:
        'min': [parseInt(minPrice.dataset.price)]
        'max': [parseInt(maxPrice.dataset.price)]

    handlesSlider.noUiSlider.on 'update', (values, handle) ->
      value = values[handle]
      if handle
        maxPrice.value = Math.round value
      else
        minPrice.value = Math.round value

    minPrice.addEventListener 'change', () ->
      handlesSlider.noUiSlider.set [this.value, null]

    maxPrice.addEventListener 'change', () ->
      handlesSlider.noUiSlider.set [null, this.value]
  # ---------------------------------------------------------------------------