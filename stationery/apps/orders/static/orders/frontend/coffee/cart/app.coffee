class CartApp extends Marionette.View
  el: '#cart-full-price'
  template: _.template "<%- price %>"
  model: ->
    cartPrice

  templateContext: ->
    price: @price

  modelEvents:
    'change:amount': 'onChangePrice'

  onChangePrice: ->
    console.log 'test'
    @render()

  initialize: (options) ->
    @price = 0
    @render()


new CartApp()
