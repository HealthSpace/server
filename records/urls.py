from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('create-ehr/',views.create_ehr,name='create-ehr'),
]
