do ($=jQuery, window, document) ->

  toPrice = (value) ->
    price = value.toFixed(2).replace /\B(?=(\d{3})+(?!\d))/g, ' '


  # JQ Plugin для animate CSS
  # ---------------------------------------------------------------------------
  $.fn.extend animateCss: (animationName, callback) ->
    animationEnd = ((el) ->
      animations = 
        animation: 'animationend'
        OAnimation: 'oAnimationEnd'
        MozAnimation: 'mozAnimationEnd'
        WebkitAnimation: 'webkitAnimationEnd'

      for t of animations
        if el.style[t] != undefined
          return animations[t]
      return

    )(document.createElement('div'))

    @removeClass 'hidden'
    @addClass('animated ' + animationName).one animationEnd, ->
      $(this).removeClass 'animated ' + animationName
      if typeof callback == 'function'
        callback()
      return
    this
  # ---------------------------------------------------------------------------


  # AUTOCOMLETE
  # ---------------------------------------------------------------------------
  $ ->
    searchBlock = $ '.header-search'

    escapeRegExChars = (value) ->
      value = value.replace /[\\^$*+?.()|[\]{}]/g, '\\$&'
      value.split(' ').filter((n) -> n != '').join '|'

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


  # ПСЕВДО HOVER НА ПОИСКОВЫЙ БЛОК
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


    $('.cart--item-delete--link').on 'click', (e) ->
      el = $ @
      $.ajax
        type: 'DELETE'
        url: '/api/orders/'
        headers: {
          'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        }
        data: {
          'offer': el.data 'deleteOfferId'
        }
        success: (data, status) =>
          el.closest('.cart--item').remove()
          $('.cart-info--price').trigger 'htmlchange'
          console.log status
        error: (data, status) =>
          console.log status
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


  # QUANTITY
  # ---------------------------------------------------------------------------
  $ ->
    $('input.quantity').on 'click', ->
      $(@).select()

    $('.cart--item-quantity input').on 'click', ->
      $(@).select()
  # ---------------------------------------------------------------------------


  # FILTERS FORM
  # ---------------------------------------------------------------------------
  $ ->
    form = $ '#offer-filter'

    $('.reset', form).on 'click', (e) ->
      e.preventDefault()
      window.location = '//' + location.host + location.pathname

    $('#id_has_rests', form).on 'change', (e) ->
      form.submit()

    $('#id_order', form).on 'change', (e) ->
      form.submit()

  # ---------------------------------------------------------------------------


  # REGISTRATION FORM
  # ---------------------------------------------------------------------------
  $ ->
    form = $ '#registration-form'
    $('input, textarea', '.field-row-company ').prop 'required', false

    $('input[name=user_type]', form).on 'change', (e) ->

      if $(this).val() == '1'
        $('.field-row-company', form).addClass 'hide'
        $('input, textarea', '.field-row-company ').prop 'required', false

      else if $(this).val() == '2'
        $('.field-row-company', form).removeClass 'hide'
        $('input, textarea', '.field-row-company ').prop 'required', true

    $('input[name=user_type]:checked', form).trigger 'change'
  # ---------------------------------------------------------------------------


  # YANDEX OFFICES MAP
  # ---------------------------------------------------------------------------
  class InitOfficeMap
    constructor: ->
      maps = []

      $('[data-coords]').each (i) ->
        maps[i] = new ymaps.Map $('.map', this)[0],
          center: $(this).data('coords')
          zoom: 17
          behaviors: [
            'drag'
            'dblClickZoom'
            'multiTouch'
          ]
          controls: [
            'fullscreenControl'
            'geolocationControl'
            'typeSelector'
            'zoomControl'
          ]

        maps[i].placemark = new ymaps.Placemark $(this).data('coords')
        maps[i].geoObjects.add maps[i].placemark

  if $('[data-coords]').length
    ymaps.ready InitOfficeMap

  # ---------------------------------------------------------------------------


  # SLIDER
  # ---------------------------------------------------------------------------
  swiper = new Swiper '.swiper-container', 
  navigation:
    nextEl: '.swiper-button-next'
    prevEl: '.swiper-button-prev'
   pagination: 
    el: '.swiper-pagination'
   clickable: true
   loop: true
   autoplay: delay: 4000
   renderBullet: (index, className) ->
      '<span class="' + className + '">' + index + 1 + '</span>'
  # ---------------------------------------------------------------------------


  # POPUP FILTER
  # ---------------------------------------------------------------------------
  $(document).ready ->
  $('.slide-toggle').click ->
    $('.mobile-hide').slideToggle()
    return
  return
  # ---------------------------------------------------------------------------

	# MASK PHONE
	# ---------------------------------------------------------------------------
	$(document).ready ->
		$('#id_phone').mask("+7 (999) 99-99-999")
		return
	#----------------------------------------------------------------------------


	# BREADCRUMS ON PHONE 
	# ----------------------------------------------------------------------------
	$(document).ready ->
		if ((window.screen.width < 480) and ($('.breadcrumbs').children("li").length) == 0)
			$('.breadcrumbs__section').css("display", "none")
		else 
			$('.breadcrumbs__section').css("display", "block")
		return		
	# ----------------------------------------------------------------------------