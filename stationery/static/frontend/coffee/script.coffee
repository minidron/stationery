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
  $ ->
    $('.menu-toggle').click ->
      $('.navbar-menu').toggleClass 'mobile-hide'

    $('.filter-toggle').click ->
      $('.category-filters').toggleClass 'mobile-hide'
  # ---------------------------------------------------------------------------

	# TOGGLE MENU
	# ---------------------------------------------------------------------------
$(document).ready ->
  if ($(window).width() > 720)
    $('.sub-menu').hide()
$('.navbar-menu--root-item').click ->
  $(this).find('.sub-menu').slideToggle()
  return
return

$(document).mouseup (e) ->
  container = $('.sub-menu')
  if !container.is(e.target) and container.has(e.target).length == 0
    return container.hide()
  return
	# ---------------------------------------------------------------------------


$(document).ready ->
  $('.sub-menu > *:nth-child(2)').hover ->
    $('.sub-menu-level-2').hide()
    $(this).find(".sub-menu-level-2:eq(0)").show()
  $('.sub-menu > *:nth-child(1)').hover ->
    $('.sub-menu-level-2').hide()
    $(this).find(".sub-menu-level-2:eq(0)").show()
  $('.sub-menu > *:nth-child(3)').hover ->
    $('.sub-menu-level-2').hide()
    $(this).find(".sub-menu-level-2:eq(0)").show()
  $('.sub-menu > *:nth-child(4)').hover ->
    $('.sub-menu-level-2').hide()
    $(this).find(".sub-menu-level-2:eq(0)").show()





		#$('.sub-menu').mouseup(a) ->
			#if !child.is(a.target) and child.has(a.target).length == 0
    		#return child.hide()

	# MASK PHONE
	# ---------------------------------------------------------------------------
$(document).ready ->
  $('#id_phone').mask("+7 (999) 999-99-99")
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

# BREADCRUMS NONE
	# ----------------------------------------------------------------------------
	$(document).ready ->
		if (($('.breadcrumbs').children("li").length) == 0)
			$('.breadcrumbs__section').css("display", "none")
		return
	# ---------------------------------------------------------------------------

# MODAL WINDOW
  #-----------------------------------------------------------------------------
  $(document).ready ->
    alert('hello')
    return
  #-----------------------------------------------------------------------------



