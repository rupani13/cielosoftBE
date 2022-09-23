from itertools import combinations_with_replacement
from locale import currency
from operator import contains
from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from account.models import Account
from djmoney.models.fields import MoneyField
# Create your models here.
class PaymentStatus:
    SUCCESS = "Success"
    FAILURE = "Failure"
    PENDING = "Pending"


class Order(models.Model):
    name = CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )

    def __str__(self):
        return f"{self.id}-{self.name}-{self.status}"

class PurchaseCoin(models.Model):
    coins                   = models.IntegerField(default=0)
    # price                   = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    price                   = models.IntegerField(default=0)
    unit                = models.CharField(default='USD', max_length=3)
    def __str__(self):
        return f"{self.unit} {self.price}"

class PurchaseOrder(models.Model):
    orderid = models.CharField(
        _("Order ID"), max_length=36, null=False, blank=False, unique=True
    )
    coins                   = models.IntegerField(default=0)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    userid = models.ForeignKey(Account, on_delete=models.CASCADE)