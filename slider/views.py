from django.shortcuts import render
from rest_framework.views import APIView
from slider.models import Slider
from slider.api.serializers import SliderSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
# Create your views here.
class SliderView(APIView):
    
    model = Slider

    def get(self, request):
        slider_list = Slider.objects.all().order_by('type_slider')
        serialzer = SliderSerializer(slider_list, context={"request": request}, many=True)
        return Response(serialzer.data)
