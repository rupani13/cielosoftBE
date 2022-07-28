from django.contrib import admin
from author.models import Author

# Register your models here.
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'book_count']

admin.site.register(Author, AuthorAdmin)