do ($=jQuery, window, document) ->

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
        result = suggestion.value + '<div class="price">' + suggestion.data.price + '</div>'
        result.replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>')

      onSelect: (suggestion) ->
          window.location.href = suggestion.data.link
  # ---------------------------------------------------------------------------
