from django.urls import path
from slider.views import SliderView

app_name = 'slider'

urlpatterns = [
	path('', SliderView.as_view()),
]
