from rest_framework import serializers
from book.models import BookDetails, Books, Chapter
from genre.api.serializers import *
from author.api.serializers import *

# Books Detials
# ------------------------------------------------
class BookDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookDetails
        fields = '__all__'


class BooksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Books
        fields = '__all__'
        

# Chapter
# ------------------------------------------------
class ChapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chapter
        fields = '__all__'
