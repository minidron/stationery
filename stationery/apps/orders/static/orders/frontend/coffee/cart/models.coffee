class CartApp.CartPrice extends Backbone.Model
  defaults:
    amount: 1

  url: ->
    "/api/orders/"

  parse: (response, options) ->
    response

  initialize: (options) ->
    @fetch()


cartPrice = new CartApp.CartPrice()
