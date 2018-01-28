class CartApp extends Marionette.View
  el: '#cart-full-price'
  template: _.template "<%- price %>"

  templateContext: ->
    price: @price

  onChangePrice: ->
    @render()

  initialize: (options) ->
    @price = 0
    @render()


new CartApp()
