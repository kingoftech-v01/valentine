from django.urls import path
from core import views

urlpatterns = [
    path("", views.create_view, name="create"),
    path("v/<str:uid>/", views.valentine_view, name="valentine"),
]
