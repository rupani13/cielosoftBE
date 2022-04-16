from django.contrib import admin
from slider.models import Slider
# Register your models here.

# admin.site.register(Slider)
@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
	list_display = ['slider_id', 'slider_url', 'type_slider']
