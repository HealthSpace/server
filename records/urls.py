from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('retrieve-ehr/',views.retrieve_ehr,name='retrieve-ehr'),
    path('add-ehr/',views.add_ehr,name='add-ehr'),
]
