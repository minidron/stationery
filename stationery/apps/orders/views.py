from django.contrib.auth.views import LoginView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order


class OrderAPIView(APIView):
    """
    API для заказов.
    """
    def get(self, request, *args, **kwargs):
        order = Order.get_cart(request.user)
        return Response({'amount': order.amount}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        order = Order.get_cart(request.user)
        order.add_item(request.POST['offer'])
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class UserLoginView(LoginView):
    template_name = 'pages/frontend/registration/login.html'
