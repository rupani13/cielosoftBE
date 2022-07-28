from unicodedata import name
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from useractivity.models import UserActivity, UserFeedback
from useractivity.api.serializers import UserActivitySerializer

# Create your views here.
# User Activity     
# ------------------------------------------------
class UserActivityView(APIView):
    
    model = UserActivity
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_activity_list = UserActivity.objects.all()
        serialzer = UserActivitySerializer(user_activity_list, many=True)
        return Response(serialzer.data)

    def post(self, request):
        serialzer = UserActivitySerializer(data=request.data)
        if serialzer.is_valid():
            serialzer.save()
            return JsonResponse(serialzer.data, status = status.HTTP_201_CREATED)
        return JsonResponse(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedbackView(APIView):
    model = UserFeedback
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        name = request.data.get('name')
        comment = request.data.get('comment')
        rating = request.data.get('rating')
        try:
            email = request.user
            UserFeedback.objects.create(email=email, name=name, comment=comment, rating=rating)
            return Response({
                "code": 200, 
            "message": "Thanks your feedback recorded"})
        except Exception:
            return Response({
                "code": 400, 
            "message": "Server Error"})

