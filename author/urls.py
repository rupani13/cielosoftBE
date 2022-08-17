from django.urls import path
from author.views import AuthorView, AuthorProfileView, WriterCreate, WriterBooks

app_name = 'author'

urlpatterns = [
    path('', AuthorView.as_view()),
	# path('createbook', AuthorBookCreate.as_view()),
	path('profile/', AuthorProfileView.as_view()),
 	path('bewriter', WriterCreate.as_view()),
	path('writerbooks', WriterBooks.as_view()),
]
