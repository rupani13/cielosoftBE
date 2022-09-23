from django.shortcuts import render
from account.models import Account
from userprofile.models import UserProfile

from order.models import Order, PaymentStatus, PurchaseCoin, PurchaseOrder
from django.views.decorators.csrf import csrf_exempt
# import razorpay
from django.conf import settings
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from order.api.serializers import PurchaseSerializer
# Create your views here.

class OrderPayment(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def order_response(self, order):
        return {
            {"status": order.status}
        }
    def post(self, request):
        # name = request.data.get("name")
        # amount = request.data.get("amount")
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # razorpay_order = client.order.create(
        #     {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
        # )
        # try:
        #     order = Order.objects.create(
        #         name=name, amount=amount, provider_order_id=razorpay_order["id"]
        #     )
        #     order.save()
        #     return Response({'order': order, "razorpay_key": settings.RAZORPAY_KEY_ID})
        # except:
        #     return Response({'error': 'Server issue while doing order. Try again after a while.', 'code': 400})
        pass

@csrf_exempt
def callback(request):
    # def verify_signature(response_data):
    #     client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    #     return client.utility.verify_payment_signature(response_data)

    # if "razorpay_signature" in request.POST:
    #     payment_id = request.POST.get("razorpay_payment_id", "")
    #     provider_order_id = request.POST.get("razorpay_order_id", "")
    #     signature_id = request.POST.get("razorpay_signature", "")
    #     order = Order.objects.get(provider_order_id=provider_order_id)
    #     order.payment_id = payment_id
    #     order.signature_id = signature_id
    #     order.save()
    #     if not verify_signature(request.POST):
    #         order.status = PaymentStatus.SUCCESS
    #         order.save()
    #         return Response({"status": order.status})
    #     else:
    #         order.status = PaymentStatus.FAILURE
    #         order.save()
    #         return Response({"status": order.status})
    # else:
    #     payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
    #     provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
    #         "order_id"
    #     )
    #     order = Order.objects.get(provider_order_id=provider_order_id)
    #     order.payment_id = payment_id
    #     order.status = PaymentStatus.FAILURE
    #     order.save()
    #     return Response({"status": order.status})
    pass

class PurchaseCoins(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def get(self, request):
        try:
            data = PurchaseCoin.objects.all().order_by('coins')
            purchase = PurchaseSerializer(data, many=True).data
        except PurchaseCoin.DoesNotExist:
            purchase = []
        return Response(purchase)

class CallBackStatus(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request):
        orderid = request.data.get("orderid")
        coin = request.data.get("coin")
        status = request.data.get("status")
        try:
            if status.upper()==PaymentStatus.SUCCESS.upper():
                purchaseorder = PurchaseOrder.objects.create(
                    orderid=orderid, coins=int(coin), status=PaymentStatus.SUCCESS, userid_id=request.user.id
                )
            elif status.upper()==PaymentStatus.PENDING.upper():
                purchaseorder = PurchaseOrder.objects.create(
                    orderid=orderid, coins=int(coin), status=PaymentStatus.PENDING, userid_id=request.user.id
                )
            else:
                return Response({'message': 'Payment is failure. we will revert your fund to you in next 7 working days.', "status": PaymentStatus.FAILURE})

            purchaseorder.save()
            userprofile = UserProfile.objects.get(user_id = request.user)
            if userprofile is not None:
                userprofile.coins =  int(userprofile.coins) + int(coin)
                userprofile.save()
            return Response({'message': 'Order is created and coins are added successfully.', "status": True})
        except:
            return Response({'error': 'Server issue while doing order. Try again after a while.', 'code': 400})
        
