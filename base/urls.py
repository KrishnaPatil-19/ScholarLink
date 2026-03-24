from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    
    path('topics/', views.topicsPage, name='topics'),
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),

    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('update-message/<str:pk>/', views.updateMessage, name='update-message'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('vote-message/<str:pk>/<str:action>/', views.voteMessage, name='vote-message'),
    path('update-user/', views.updateUser, name='update-user'),
    path('activity/', views.activityPage, name='activity'),
]
