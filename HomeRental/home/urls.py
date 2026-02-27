from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home_list'),
    path('homes/', views.home_list, name='homes'),
    path('create/', views.home_create, name='home_create'),
    path('<int:home_id>/edit/', views.home_edit, name='home_edit'),
    path('<int:home_id>/delete/', views.home_delete, name='home_delete'),
    path('register/', views.register, name='register'),
    path('property/', views.add_property, name='property'),
    path('properties/', views.property_list, name='properties'),
    path('properties/<int:property_id>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:property_id>/delete/', views.property_delete, name='property_delete'),

] 
