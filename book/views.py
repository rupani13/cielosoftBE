from errno import errorcode
from logging import error
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)

from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
)
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from book.models import (Books, Chapter, BookDetails, BookStatus, State)
from author.models import Author
from book.api.serializers import (BookDetailsSerializer, BooksSerializer, ChapterSerializer)
from tools.pagination import StandardResultsSetPagination
from account.models import Account
from comment.models import Comments
from usercollection.models import UserCollection
from useractivity.models import UserActivity
from userprofile.models import UserProfile
from userprofile.api.serializers import UserProfileSerializer
from comment.api.serializers import CommentsSerializer
from tools.customserializers import BookLatestSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from.forms import ChapterForm
from genre.models import Genre
# Create your views here.
# Books Detials
# -----------------------------------------------
class BookDetailsView(RetrieveAPIView):

    queryset = BookDetails.objects.all()
    serializer_class = BookDetailsSerializer
    lookup_field = 'pk'

    def post(self, request):
        serialzer = BookDetailsSerializer(data=request.data)
        if serialzer.is_valid():
            serialzer.save()
            return JsonResponse(serialzer.data, status = status.HTTP_201_CREATED)
        return JsonResponse(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)

# Books        
# http://127.0.0.1:8000/api/book/?limit=10&offset=0&page=1
# ------------------------------------------------
# class BooksView(ListAPIView):

#     queryset = Books.objects.all().order_by('id')
#     serializer_class = BooksSerializer
    # pagination_class = LimitOffsetPagination

class BooksView(APIView):

    pagination_class = StandardResultsSetPagination
    filterset_fields = ['genre', 'language', 'author', 'ranking', 'view', 'published_time', 'book_name']
    filter_backends = [DjangoFilterBackend]

    def get(self, request):

        def filter_queryset(queryset):
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)
            return queryset
        paginator = Paginator(filter_queryset(Books.objects.all()), 20)
        page = request.query_params.get('page')
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = []
        except EmptyPage:
            books = []
        BooksSerializer.Meta.fields = ['id', 'book_name', 'book_cover_url']
        data = BooksSerializer(books, many=True, context={"request": request}).data
        return Response(data)


class BookInfoView(APIView):
    # api/book/bookinfo/
    def post(self, request):
        books = Books.objects.filter(id=request.data.get('bookid'),
                                book_name=request.data.get('bookname'))
        class CommentSerializer(CommentsSerializer):
            email = serializers.CharField(source = 'user_id.email')
            username = serializers.CharField(source = 'user_id.username')
        class BookSerializer(BooksSerializer):
            upvote = serializers.CharField(source='book_details.upvote')
            downvote = serializers.CharField(source='book_details.downvote')
            comments = CommentSerializer(many=True, read_only=True)
            genre = serializers.CharField(source='genre.genre_name')
            author = serializers.CharField(source='author.account.name')
        BookSerializer.Meta.fields = ['id', 'chapters', 'book_name', 'book_cover_url', 'view', 'upvote', 'downvote', 'book_brief_info', 'genre', 'author', 'ranking', 'comments']
        data = BookSerializer(books, many=True, context={"request": request}).data
        return Response(data)

# class BooksSearchView(ListAPIView):
    
#     queryset = Books.objects.all()
#     serializer_class = BooksSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['book_name', 'author__author_name']


class BookReadView(APIView):
    model = Chapter
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def searchBook(self, _id, _name):
        try:
            book = Books.objects.get(id=_id)
            if book.book_name == _name:
                return True
            return False
        except Books.DoesNotExist:
            return False

    def searchBookChapter(self, _book_id, _chapter):
        try:
            _chapter = Chapter.objects.get(book_id=_book_id, chapter_no=_chapter)
            return _chapter
        except Chapter.DoesNotExist:
            return None

    def searchBookInUserActivity(self, _id, _book_id, _chapter):
        try:
            useractivity = UserActivity.objects.get(user_id=_id, book_id_id=_book_id, chapter= _chapter)
            return useractivity
        except UserActivity.DoesNotExist:
            return None
    
    def searchBookInUserCollection(self, _id, _book_id):
        try:
            _collection = UserCollection.objects.get(user_id=_id, book_id_id=_book_id)
            return True
        except UserCollection.DoesNotExist:
            return False
        
    def post(self, request):
        bookid = request.data.get('bookid')
        bookname = request.data.get('bookname')
        chapter_no = request.data.get('chapter')

        if request.user is not None:
            if BookReadView.searchBook(self, bookid, bookname):
                _chapter = BookReadView.searchBookChapter(self, bookid, chapter_no)
                if _chapter is not None:
                    if not BookReadView.searchBookInUserCollection(self, request.user, bookid):
                        book = Books.objects.get(id=bookid)
                        UserCollection.objects.get_or_create(user=request.user, book_id=book)
                    chapter = ChapterSerializer(_chapter, context={"request": request}).data
                    if BookReadView.searchBookInUserActivity(self, request.user, bookid, chapter_no) is not None:
                        return Response({'message': 'Successfully Opened.','login': True, 'unlock': True,'chapter':chapter })
                    if chapter['state'] == 'free':
                        user_act_obj, user_act_created  = UserActivity.objects.get_or_create(user_id=request.user, book_id_id=bookid, chapter = chapter_no)
                        if user_act_created:
                            user_act = UserActivity.objects.get(user_id=request.user, book_id_id=bookid, chapter=chapter_no)
                            user_act.unlocked_chapter = True
                            user_act.save()
                            return Response({'message': 'Successfully Opened.','login': True, 'unlock': True,'chapter':chapter })  
                        return Response({'message': 'Server Issue.','login': True, 'unlock': False})                                 
                    return Response({'message': 'To Unlock the new chapter, You have to earn coins.','login': True, 'unlock': False})
                else:
                    return Response({'message': 'chapter doesnt exist','login': True, 'unlock': False})
            else:
               return Response({'message': 'select the appropriate book','login': True, 'unlock': False})
        else:
            return Response({'message': 'Please login first','login': False})


class AddNewBook(APIView):
    # api/book/addNew
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    def post(self, request):
        book_name = request.data.get('bookname')
        book_cover_url = request.data.get('bookCoverUrl')
        book_brief_info = request.data.get('bookInfo')
        genre = request.data.get('genre').capitalize()
        language = request.data.get('language')
        genre_obj = Genre.objects.get(genre_name = genre)
        book_preface = request.data.get('book_intro')
        author_intro = request.data.get('author_intro')
        book_copyright = request.data.get('copyright')
        book_acknowledgement = request.data.get('acknowledgement')
        policy_agreement = request.data.get('policy_agreement')
        try:
            author = Author.objects.get(account_id=request.user.id)
            author.into = author_intro
            author.save()
            if request.data.get('bookid'):
                bookobj = Books.objects.get(author=request.user.id, id=request.data.get('bookid'))
                bookobj.book_name = book_name
                bookobj.book_cover_url = book_cover_url
                bookobj.book_brief_info = book_brief_info
                bookobj.genre_id = genre_obj.id
                bookobj.language = language.capitalize()
                bookobj.status = BookStatus.review
                bookobj.book_preface = book_preface
                bookobj.book_copyright = book_copyright
                bookobj.book_acknowledgement = book_acknowledgement
                bookobj.policy_agreement = policy_agreement
                bookobj.save()
            else:
                bookdetails_obj = BookDetails.objects.create(view=0,upvote=0,downvote=0)
                bookobj = Books.objects.create(book_name=book_name, book_cover_url = book_cover_url,
                                    book_brief_info = book_brief_info,genre_id = genre_obj.id,
                                    language = language, status = BookStatus.draft, author_id=author.id, 
                                    book_details_id=bookdetails_obj.id,
                                    book_preface=book_preface, book_copyright=book_copyright, 
                                    book_acknowledgement=book_acknowledgement, 
                                    policy_agreement=policy_agreement)
            book_data = BooksSerializer(bookobj).data

        except Author.DoesNotExist:
            book_data = {"message": "Turn on your writer mode first"}
        return Response(book_data)
    
class AddNewChapter(APIView):
    # api/book/addNewChapter
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        chapter_no = request.data.get('chapterno')
        chapter_name = request.data.get('chaptername')
        chapter_url = request.data.get('chapterurl')
        book_id = request.data.get('bookid')
        try:
            
            bookobj = Books.objects.get(id=request.data.get('bookid'))
            try:
                chapter_obj = Chapter.objects.get(book_id=book_id,
                                                     chapter_no=chapter_no)
                chapter_obj.chapter_name=chapter_name
                chapter_obj.chapter_url=chapter_url
                chapter_obj.save()
            except Chapter.DoesNotExist:
                print("not book")
                chapter_obj = Chapter.objects.create(chapter_no=chapter_no,chapter_name=chapter_name,
                                                    chapter_url=chapter_url,
                                       book_id_id=bookobj.id, 
                                       state= State.free if int(chapter_no) <=5 else State.locked) 
            chapter_serializer = ChapterSerializer(chapter_obj).data
            chapter_count = Chapter.objects.filter(book_id=book_id)
            bookobj.chapters = len(chapter_count)
            bookobj.save()
        except Books.DoesNotExist:
            chapter_serializer = {"message": "Book does not exist."}
        return Response(chapter_serializer)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
# api/book/upvote/
def upvote(request):
    '''
    increases the upvote by 1
    '''
    bookname = request.data.get('bookname')
    bookid = request.data.get('bookid')
    try:
        book = Books.objects.select_related('book_details').get(id=bookid, book_name=bookname)
    except Books.DoesNotExist:
        return Response('no book exists')
    bookdetail = BookDetails.objects.get(id=book.book_details.id)
    upvote_count = int(bookdetail.upvote) + 1
    bookdetail.upvote = upvote_count
    bookdetail.save()
    book = Books.objects.get(book_name=bookname, id=bookid)
    class CommentSerializer(CommentsSerializer):
            email = serializers.CharField(source = 'user_id.email')
            username = serializers.CharField(source = 'user_id.username')
    class BookSerializer(BooksSerializer):
            upvote = serializers.CharField(source='book_details.upvote')
            downvote = serializers.CharField(source='book_details.downvote')
            comments = CommentSerializer(many=True, read_only=True)
            author = serializers.CharField(source='author.id')
    BookSerializer.Meta.fields = ['id', 'book_name', 'book_cover_url', 'view', 'upvote', 'downvote', 'book_brief_info', 'genre', 'author', 'ranking', 'comments']
    data = BookSerializer(book).data
    return Response(data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
# api/book/downvote/
def downvote(request):
    '''
    increases the upvote by 1
    '''
    bookname = request.data.get('bookname')
    bookid = request.data.get('bookid')
    try:
        book = Books.objects.select_related('book_details').get(id=bookid, book_name=bookname)
    except Books.DoesNotExist:
        return Response('no book exists')
    bookdetail = BookDetails.objects.get(id=book.book_details.id)
    downvote_count = int(bookdetail.downvote) + 1
    bookdetail.downvote = downvote_count
    bookdetail.save()
    book = Books.objects.get(book_name=bookname, id=bookid)
    
    class CommentSerializer(CommentsSerializer):
            email = serializers.CharField(source = 'user_id.email')
            username = serializers.CharField(source = 'user_id.username')
    class BookSerializer(BooksSerializer):
            upvote = serializers.CharField(source='book_details.upvote')
            downvote = serializers.CharField(source='book_details.downvote')
            comments = CommentSerializer(many=True, read_only=True)
            author = serializers.CharField(source='author.id')
    BookSerializer.Meta.fields = ['id', 'book_name', 'book_cover_url', 'view', 'upvote', 'downvote', 'book_brief_info', 'genre', 'author', 'ranking', 'comments']
    data = BookSerializer(book).data
    return Response(data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
# api/book/comment/
def comment(request):
    '''
    increases the upvote by 1
    '''
    bookname = request.data.get('bookname')
    bookid = request.data.get('bookid')
    comment = request.data.get('comment')
    try:
        book = Books.objects.get(book_name=bookname, id=bookid)
    except Books.DoesNotExist:
        return Response('no book exists')
    Comments.objects.create(book_id=book, user_id=request.user, comment=comment)
    class CommentSerializer(CommentsSerializer):
            email = serializers.CharField(source = 'user_id.email')
            username = serializers.CharField(source = 'user_id.username')
    class BookSerializer(BooksSerializer):
            upvote = serializers.CharField(source='book_details.upvote')
            downvote = serializers.CharField(source='book_details.downvote')
            comments = CommentSerializer(many=True)
            author = serializers.CharField(source='author.id')
    BookSerializer.Meta.fields = ['id', 'book_name', 'book_cover_url', 'view', 'upvote', 'downvote', 'book_brief_info', 'genre', 'author', 'ranking', 'comments']
    data = BookSerializer(book).data
    return Response(data)


@api_view(['POST'])
def search(request):
    bookname = request.data.get('bookname')
    authorname = request.data.get('authorname')
    if bookname:
        data = BookLatestSerializer(Books.objects.filter(book_name__icontains = bookname), context={"request": request}, many=True).data
    elif authorname:
        data = []
        accounts = Account.objects.filter(name__icontains=authorname)
        for acc  in accounts:
            authors = Author.objects.filter(account = acc).values_list('id', flat=True)
            for item in authors:
                books = BookLatestSerializer(Books.objects.filter(author = item), many=True, context={"request": request}).data
                data.append(books)
    return Response(data)

# get the latest books deal
class LatestView(APIView):
    def get(self, request):
        data = dict()
        data['latest'] = BookLatestSerializer(Books.objects.all().order_by('published_time')[:5], context={"request": request}, many=True).data
        data['deals'] = BookLatestSerializer(Books.objects.all().order_by('ranking')[:5], context={"request": request}, many=True).data
        return Response(data)
  
# unlock the locked chapter
class UnLockBookChapterView(APIView):
    
    model = Chapter
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def searchBook(self, _id, _name):
        try:
            book = Books.objects.get(id=_id)
            if book.book_name == _name:
                return True
            return False
        except Books.DoesNotExist:
            return False

    def searchBookInUserActivity(self, _id, _book_id, _chapter):
        try:
            useractivity = UserActivity.objects.get(user_id=_id, book_id_id=_book_id, chapter= _chapter)
            return useractivity
        except UserActivity.DoesNotExist:
            return None

    def post(self, request):
        coins = request.data.get('coins')
        bookid = request.data.get('bookid')
        bookname = request.data.get('bookname')
        chapter_no = request.data.get('chapter')

        if request.user is not None:
            # coincheck if the coins exist in his userprofile and check user too
            try:
                userprofile = UserProfile.objects.get(user_id = request.user)
                if userprofile is not None:
                    print(userprofile)
                    if UnLockBookChapterView.searchBook(self, bookid, bookname):
                        #save the updated coins
                        # add this in UserActivity
                        if UnLockBookChapterView.searchBookInUserActivity(self, request.user, bookid, chapter_no) is not None:
                            return Response({'message': 'Chapter is already unlocked', 'login': True, 'unlock': True})  
                
                        if userprofile.coins >= int(coins):
                            user_act_obj, user_act_created = UserActivity.objects.get_or_create(user_id=request.user, book_id_id=bookid, chapter=chapter_no)
                            if user_act_created:
                                user_act = UserActivity.objects.get(user_id=request.user, book_id_id=bookid, chapter=chapter_no)
                                user_act.unlocked_chapter = True
                                user_act.chapter = chapter_no
                                user_act.save()
                                userprofile.coins = userprofile.coins - int(coins)
                                userprofile.save()              
                                return Response({'message': 'Successfully unlock the chapter', 'login': True, 'unlock': True})
                            return Response({'message': 'Chapter is already unlocked', 'login': True, 'unlock': True})
                        return Response({'message': 'You dont have enough coins. Earned them or Buy coins', 'login': True, 'unlock': False})
                    return Response({'message': 'Select appropriate book', 'login': True, 'unlock': False})
                return Response({'message':'Kindly create the profile with coins', 'login': False, 'unlock': False})
            except UserProfile.DoesNotExist:
                return Response({'message':'No Such user exist. Kindly login first. Or Server issue','login': False, 'unlock': False})
        return Response({'message': 'No Such user exist. Kindly login first.', 'login': False, 'unlock': False})


class BookmarkBook(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            book = Books.objects.filter(bookmark=request.user)
        except Books.DoesNotExist:
            book = []
        return Response(BooksSerializer(book, many=True).data)

    def post(self, request):
        bookid = request.data.get('bookid')
        print(bookid)
        try:
            book = Books.objects.get(id=bookid)
            try:
                book = Books.objects.get(id=bookid, bookmark__id=request.user.id)
                book.bookmark.remove(Account.objects.get(id = request.user.id))
            except Books.DoesNotExist:
                book.bookmark.add(Account.objects.get(id = request.user.id))  
            book = Books.objects.filter(bookmark__id=request.user.id)
            return Response(BooksSerializer(book, many=True).data)
        except Books.DoesNotExist:
            book = {'message': 'Book does not exist. You cannot bookmark this.', 'error': 400}
            return Response(book)

class ChaptersByBook(APIView):
    def post(self, request):
        BooksSerializer.Meta.fields = ['book_preface', 'book_copyright', 'book_acknowledgement']
        try:
            book = Books.objects.get(id=request.data.get('bookid'))
            book_response = BooksSerializer(book).data
            try:
                ChapterSerializer.Meta.fields = ['chapter_no', 'chapter_name', 'state']
                data = Chapter.objects.filter(book_id = book)
                response = {**book_response, 'chapter':  ChapterSerializer(data, many=True).data}
            except Chapter.DoesNotExist:
                response = {**book_response, 'chapter': []}
        except Books.DoesNotExist:
            response = {'error': 'Kindly Select the apporiate book.', 'code': 400}
        return Response(response)
