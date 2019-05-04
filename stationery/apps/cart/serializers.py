from rest_framework import serializers


class ItemSSerializer(serializers.Serializer):
    """
    Сериализатор для модели `Товар в заказе`.
    """
    offer_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=1)
