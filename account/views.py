#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from contextlib import nullcontext
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from account.api.serializers import RegistrationSerializer, \
    AccountPropertiesSerializer, ChangePasswordSerializer
from account.models import Account
from rest_framework.authtoken.models import Token
from userprofile.models import UserProfile
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import COUNTRY_CODE_TO_REGION_CODE, \
    national_significant_number, region_code_for_number

import requests
import backoff
from django.conf import settings


# Create your views here.

# Register

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def registration_view(request):
    if request.method == 'POST':
        data = {}
        email = request.data.get('email', '0').lower()
        username = request.data.get('username', '0')
        name = request.data.get('name', '0')
        password = request.data.get('password', '0')
        password2 = request.data.get('password2', '0')
        if validate_email(email) != None:
            data['error_message'] = 'That email is already in use.'
            data['code'] = 400
            return Response(data, 400)
        if validate_username(username) != None:
            data['error_message'] = 'That username is already in use.'
            data['code'] = 400
            return Response(data, 400)

        payload = {
            'email': email,
            'username': username,
            'password': password,
            'password2': password2,
            'name': name,
            }
        response = create_new_user(payload)
        return Response(response)


def create_new_user(payload):
    data = {}
    serializer = RegistrationSerializer(data=payload)
    if serializer.is_valid():
        account = serializer.save()
        data['response'] = 'successfully registered new user.'
        data['email'] = account.email
        data['username'] = account.username
        data['pk'] = account.pk
        token = Token.objects.get(user=account).key
        data['token'] = token
        UserProfile.objects.create(user_id=account)
    else:
        data = serializer.errors
    return data


def validate_mobileno(phone, code):
    phoneno = to_python(phone, region=code)
    if phoneno and not phoneno.is_valid():
        return False
    for (prefix, values) in COUNTRY_CODE_TO_REGION_CODE.items():
        if code in values and prefix == phoneno.country_code:
            return True
    return False


def validate_email(email):
    account = None
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return None
    if account != None:
        return email


def validate_username(username):
    account = None
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None
    if account != None:
        return username


# Account properties
# Url: https://<your-domain>/api/account/
# Headers: Authorization: Token <token>

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def account_properties_view(request):

    try:
        account = request.user
    except Account.DoesNotExist:
        data = {
            'error': 'Account does not exist',
            'code': status.HTTP_404_NOT_FOUND
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AccountPropertiesSerializer(account)
        return Response(serializer.data)


# Account update properties
# Url: https://<your-domain>/api/account/properties/update
# Headers: Authorization: Token <token>

@api_view(['PUT'])
@permission_classes((IsAuthenticated, ))
def update_account_view(request):

    try:
        account = request.user
    except Account.DoesNotExist:
        data = {
            'error': 'Account does not exist',
            'code': status.HTTP_404_NOT_FOUND
        }
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        
        serializer = AccountPropertiesSerializer(account,
                data=request.data)

        data = {}
        if serializer.is_valid():
            serializer.save()
            data['message'] = 'Account updated successfully.'
            return Response(data=data)
        data['error'] = serializer.errors
        data['code'] = status.HTTP_400_BAD_REQUEST
        return Response(data=data)


# LOGIN
# URL: /api/account/login

class ObtainAuthTokenView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {}

        email = request.data.get('username', '0')
        password = request.data.get('password', '0')
        account = authenticate(email=email, password=password)
        if account:
            try:
                token = Token.objects.get(user=account)
            except Token.DoesNotExist:
                token = Token.objects.create(user=account)
            context['message'] = 'Successfully authenticated.'
            context['pk'] = account.pk
            context['email'] = email.lower()
            context['token'] = token.key
            context['username'] = account.username
        else:
            context['code'] = 400
            context['error'] = 'Invalid credentials'

        return Response(context)


@api_view(['GET'])
@permission_classes([])
@authentication_classes([])
def does_account_exist_view(request):

    if request.method == 'GET':
        email = request.GET['email'].lower()
        data = {}
        try:
            account = Account.objects.get(email=email)
            data['message'] = email
        except Account.DoesNotExist:
            data['code'] = 400
            data['error'] = 'Account does not exist'
        return Response(data)


class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = Account
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(
        self,
        request,
        *args,
        **kwargs
        ):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            # Check old password

            if not self.object.check_password(serializer.data.get('old_password'
                    )):
                return Response({'error': ['Wrong password.'], 'code': 400},
                                status=status.HTTP_400_BAD_REQUEST)

            # confirm the new passwords match

            new_password = serializer.data.get('new_password')
            confirm_new_password = \
                serializer.data.get('confirm_new_password')
            if new_password != confirm_new_password:
                return Response({'new_password': ['New passwords must match'
                                ], 'code': 400}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get

            self.object.set_password(serializer.data.get('new_password'
                    ))
            self.object.save()
            return Response({'message': 'successfully changed password'
                            }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST', ))
@permission_classes([])
@authentication_classes([])
def login_firebase_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    provider = request.data.get('provider')
    token = request.data.get('token')
    try: 
        data = proceed_to_login(request, email,
                                    username, token, provider)
    except Exception:
        return Response(error_response(400), status=status.HTTP_400_BAD_REQUEST)
    return Response(data, 200)
    # print ('login_firebase_view')
    # firbase_dict = load_data_from_firebase_api(token)
    # print (firbase_dict)
    # if 'users' in firbase_dict:
    #     user = firbase_dict['users']

    #     if len(user) > 0:
    #         user_one = user[0]
    #         if 'phoneNumber' in user_one:
    #             if user_one['phoneNumber'] == email:
    #                 data = proceed_to_login(request, email, username,
    #                         token, provider)

    #                 return Response(data, 200)
    #             else:
    #                 return Response(data, 200)
    #         else:
    #             if email == user_one['email']:
    #                 provider1 = user_one['providerUserInfo'
    #                         ][0]['providerId']
    #                 if user_one['emailVerified'] == 1 \
    #                     or user_one['emailVerified'] == True \
    #                     or user_one['emailVerified'] == 'True' \
    #                     or provider1 == 'facebook.com':
    #                     data = proceed_to_login(request, email,
    #                             username, token, provider)
    #                     return Response(data, 200)
    #                 else:
    #                     return Response(error_response(403),
    #                             status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                 return Response(error_response(402),
    #                                 status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response(error_response(401),
    #                         status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response(firbase_dict)


def error_response(code):
    switcher = {400: 'Invalid Request User Not Found.',
                402: 'Unknown Email User.',
                403: 'Please Verify Your Email to Get Login.'}
    return {'error': switcher(code), 'code': 400}

@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=5,
    giveup=lambda e: e.response is not None and e.response.status_code < 500
)
def load_data_from_firebase_api(token):
    url = settings.API_URL
    payload = 'key=' + settings.API_KEY + '&idToken=' + token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=5, verify=True)
        return response.json()
    except requests.exceptions.ConnectionError:
        return {'code': 500, 'error': 'Connection refused'}
    
def proceed_to_login(
    request,
    email,
    username,
    token,
    provider,
    ):
    payload = {
		"email": request.data.get("email"),
		"username": request.data.get("username"),
		"name": request.data.get("username"),
		"password": username+"ZZ_bookatease",
		"password2":username+"ZZ_bookatease"
	}
    context = {}
    if validate_email(email) != None:

        account = Account.objects.get(email=email)
        token_server = Token.objects.get(user=account)
        context['message'] = 'Successfully authenticated.'
        context['pk'] = account.pk
        context['email'] = email
        context['token'] = token_server.key
        context['username'] = account.username
        return context
    else:
        data = create_new_user(payload)
        return data

    
