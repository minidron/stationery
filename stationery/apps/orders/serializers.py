from rest_framework import serializers

from orders.models import Item, Order, OrderStatus


class FieldsMixin:
    """
    Делаем возможность указывать поля, необходимые для сериализации.

    Пример:
    ModelSerializer(context={'fields': [список_полей]})
    """

    def __init__(self, *args, **kwargs):
        self.display_fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

    def get_field_names(self, *args, **kwargs):
        field_names = self.display_fields
        if field_names:
            return field_names
        return super().get_field_names(*args, **kwargs)


class ItemSerializer(FieldsMixin, serializers.ModelSerializer):
    """
    Сериализатор для модели `Товар в заказе`.
    """
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'offer', 'quantity', 'unit_price', 'total_price']


class OrderSerializer(FieldsMixin, serializers.ModelSerializer):
    """
    Сериализатор для модели `Заказ`.
    """
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)
    items = ItemSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'amount', 'items']

    def get_status(self, obj):
        """
        Получаем статус заказа в MACHINE_NAME.
        """
        return OrderStatus.CHOICES_MACHINE_NAME[obj.status]


class AddressSerializer(serializers.Serializer):
    """
    Сериализатор для объекта `Адрес`.
    """
    address = serializers.CharField(max_length=255)
    zip_code = serializers.CharField(max_length=6)
