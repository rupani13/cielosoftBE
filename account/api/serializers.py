from rest_framework import serializers
from account.models import Account
from django_countries import Countries

class SerializableCountryField(serializers.ChoiceField):
    def __init__(self, **kwargs):
        super(SerializableCountryField, self).__init__(choices=Countries())

    def to_representation(self, value):
        if value in ('', None):
            return '' # normally here it would return value. which is Country(u'') and not serialiable
        return super(SerializableCountryField, self).to_representation(value)
class RegistrationSerializer(serializers.ModelSerializer):

	password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

	class Meta:
		model = Account
		fields = ['email', 'username', 'password', 'password2', 'name']
		extra_kwargs = {
				'password': {'write_only': True},
		}	

	def	save(self):
		account = Account(
					email=self.validated_data['email'],
					username=self.validated_data['username'],
					name=self.validated_data['name']
				)
		password = self.validated_data['password']
		password2 = self.validated_data['password2']
		if password != password2:
			raise serializers.ValidationError({'password': 'Passwords must match.'})
		account.set_password(password)
		account.save()
		return account

	

class AccountPropertiesSerializer(serializers.ModelSerializer):
	nationality = SerializableCountryField(allow_blank=True, choices=Countries())
	class Meta:
		model = Account
		fields = ['pk', 'email', 'username', 'name', 'nationality', 'birth_date', 'phone']


class ChangePasswordSerializer(serializers.Serializer):

	old_password 				= serializers.CharField(required=True)
	new_password 				= serializers.CharField(required=True)
	confirm_new_password 		= serializers.CharField(required=True)
