from rest_framework import serializers


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class PaymentCompleteSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["SUCCESS", "FAILED"])
    transaction_id = serializers.CharField(required=False)
