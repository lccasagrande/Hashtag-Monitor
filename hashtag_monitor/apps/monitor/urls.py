from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path("", views.index, name='index'),
    path("hashtag/delete/<str:name>", views.hashtag_delete, name='hashtag_delete'),
    path("hashtag/create", views.hashtag_create, name='hashtag_create')
]
