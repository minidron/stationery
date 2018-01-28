class CartApp.CartPrice extends Backbone.Model
  defaults:
    amount: 0

  url: ->
    "/api/orders/"


cartPrice = new CartApp.CartPrice()
