from django.contrib import admin
from book.models import Books, BookDetails, Chapter


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_name', 'chapters', 'genre', 'author', 'status', 'book_details')

class BookDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'view', 'upvote', 'downvote')

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter_no', 'chapter_name', 'book_id', 'coins')
# Register your models here.
admin.site.register(Books, BookAdmin)
admin.site.register(BookDetails, BookDetailsAdmin)
admin.site.register(Chapter, ChapterAdmin)
