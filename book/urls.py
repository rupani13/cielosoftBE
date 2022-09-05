from django.urls import path
from book.views import (BookDetailsView, AddNewBook, BooksView, BookReadView, 
BookInfoView, upvote, downvote, comment, search, LatestView, UnLockBookChapterView, AddNewChapter,
BookmarkBook, ChaptersByBook, DeleteBook, WriterBooks)

app_name = 'book'

urlpatterns = [
	path('bookDetails/<int:pk>', BookDetailsView.as_view()),
    path('', BooksView.as_view()),
    # path('search/', BooksSearchView.as_view()),
    path('addNew', AddNewBook.as_view()),
    path('bookread/', BookReadView.as_view()),
    path('bookinfo/', BookInfoView.as_view()),
    path('upvote/', upvote),
    path('downvote/', downvote),
    path('comment/', comment),
    path('search/', search),
    path('latest/', LatestView.as_view()),
    path('unlockbookchapter/', UnLockBookChapterView.as_view()),
    path('addNewChapter', AddNewChapter.as_view()),
    path('bookmark', BookmarkBook.as_view()),
    path('chaptersByBook', ChaptersByBook.as_view()), 
    path('deleteBook', DeleteBook.as_view()),
    path('writerbooks', WriterBooks.as_view()),
]
