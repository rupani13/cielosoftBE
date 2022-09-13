from django.contrib import admin
from order.models import Order, PurchaseCoin


# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'status')

admin.site.register(Order, OrderAdmin)

class PurchaseCoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'coins', 'price', 'currency')

admin.site.register(PurchaseCoin, PurchaseCoinAdmin)