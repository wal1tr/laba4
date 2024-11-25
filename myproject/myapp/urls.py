from django.urls import path
from . import views

app_name = 'myapp'  # Убедитесь, что это строка есть

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('add/', views.recipe_form, name='recipe_form'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/', views.download_recipes_xml, name='download_recipes_xml'),  # Добавьте эту строку
]
