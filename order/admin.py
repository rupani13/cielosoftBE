from django.contrib import admin
from order.models import Order, PurchaseCoin, PurchaseOrder


# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'status')

admin.site.register(Order, OrderAdmin)

class PurchaseCoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'coins', 'price', 'unit')

admin.site.register(PurchaseCoin, PurchaseCoinAdmin)


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'orderid', 'coins', 'status', 'userid')

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)