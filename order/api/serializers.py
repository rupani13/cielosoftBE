
from rest_framework import serializers
from order.models import PurchaseCoin


# Comments
# ------------------------------------------------
class PurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseCoin
        fields = '__all__'