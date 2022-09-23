
from django.urls import path
from django.contrib import admin
from order.views import callback, OrderPayment, PurchaseCoins

urlpatterns = [
	path("payment/", OrderPayment.as_view(), name="payment"),
    path("callback/", callback, name="callback"),
    path("purchase/", PurchaseCoins.as_view(), name="purchase"),
]