from rest_framework import serializers
from account.models import Account
from author.models import Author
from book.api.serializers import BooksSerializer


class AuthorProfileSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="account.name")
    class Meta:
        model = Author
        fields = ['id', 'author_name', 'intro', 'hobbies', 'profilepicture']


class AuthorSerializer(serializers.ModelSerializer):

    books = BooksSerializer(many=True, read_only=True)
    author_name = serializers.ReadOnlyField(source="account.name")
    class Meta:
        model = Author
        fields = ['id', 'author_name', 'intro', 'hobbies', 'profilepicture', 'books']

# class WriterSerializer(serializers.ModelSerializer):
    
#     books = BooksSerializer(many=True, read_only=True)
#     #author_name = serializers.ReadOnlyField(source="account.name")
#     class Meta:
#         model = Author
#         fields = ['books']
