from django.urls import path
from danfe.views import index

app_name = 'danfe'
urlpatterns = [
    path('', index, name='index'),
]
