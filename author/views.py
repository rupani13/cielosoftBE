from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
)
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from author.models import Author
from author.api.serializers import AuthorSerializer, AuthorProfileSerializer
from tools.pagination import StandardResultsSetPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.
# Author
# http://127.0.0.1:8000/api/authors/?limit=10&offset=10&page=1
# -----------------------------------------------
class AuthorView(ListAPIView):
    queryset = Author.objects.all().order_by('id')
    serializer_class = AuthorSerializer
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        StandardResultsSetPagination.page_size=10
        serializer = AuthorSerializer(Author.objects.all().order_by('id'), context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

# class AuthorBookCreate(APIView):
#     def post(self, request):
#         authorId = request.data.get('author')
#         data = AuthorSerializer(Author.objects.get(id=authorId), context={"request": request}).data
#         return Response(data)

class AuthorProfileView(APIView):
    # def get(self, request):
    #     author_list = Author.objects.all()
    #     serialzer = AuthorSerializer(author_list, many=True)
    #     return Response(serialzer.data)

    # def post(self, request):
    #     serialzer = AuthorProfileSerializer(data=request.data)
    #     if serialzer.is_valid():
    #         #serialzer.save()
    #         return JsonResponse(serialzer.data, status = status.HTTP_201_CREATED)
    #     return JsonResponse(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        data = AuthorSerializer(Author.objects.all(), context={"request": request}, many=True).data
        return Response(data)

    def post(self, request):
        data = AuthorSerializer(Author.objects.get(id=request.data.get('author')), context={"request": request}).data
        return Response(data)

class WriterCreate(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def get(self, request):
        toggle = request.query_params.get('writer')
        if toggle:
            try:
                data = Author.objects.get(account_id=request.user.id)
            except Author.DoesNotExist:
                data = Author.objects.create(account_id = request.user.id)
            response_data = AuthorSerializer(data, context={"request": request}).data  
        else:
            response_data = {"message": "You have Reader permission only"}
        return Response(response_data)