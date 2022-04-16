from rest_framework import serializers
from slider.models import Slider

# UserActivity
# ------------------------------------------------
class SliderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slider
        fields = '__all__'
