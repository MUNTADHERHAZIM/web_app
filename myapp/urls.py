from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('search/', views.search_articles, name='search'),
    path('profile/', views.user_profile, name='user_profile'),
    path('article/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter/confirm/<str:token>/', views.confirm_subscription, name='confirm_subscription'),
    path('article/<slug:slug>/track/', views.track_reading_progress, name='track_reading_progress'),
    path('article/<slug:slug>/pdf/', views.generate_pdf, name='generate_pdf'),
]
