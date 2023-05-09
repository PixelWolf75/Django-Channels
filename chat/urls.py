# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.HomePage.as_view(), name='home'),
    path('old_room/<int:room_name>/', views.room, name='room'),
    path('login', views.LoginPage.as_view(), name='login'),
]
