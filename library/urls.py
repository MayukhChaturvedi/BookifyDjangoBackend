from django.urls import path
from .views import author_list_create, author_detail, book_list_create, book_detail, genre_list_create, genre_detail, book_instance_list_create, book_instance_detail, rag_query
from .auth_views import register, login
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("authors/", author_list_create, name="author-list"),
    path("authors/<str:author_id>/", author_detail, name="author-detail"),
    path("books/", book_list_create, name="book-list"),
    path("books/<str:book_id>/", book_detail, name="book-detail"),
    path("genres/", genre_list_create, name="genre-list"),
    path("genres/<str:genre_id>/", genre_detail, name="genre-detail"),
    path("book-instances/", book_instance_list_create, name="book-instance-list"),
    path("book-instances/<str:book_instance_id>/", book_instance_detail, name="book-instance-detail"),
    path("auth/register/", register, name="register"),
    path("auth/login/", login, name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('rag/', rag_query, name='rag_query'),
]