from django.conf.urls import url
from . import views

app_name = 'api'
urlpatterns = [
    url(r'^getcurrentjuried/$', views.GetCurrentDances, name='getcurrentjuried'),
    url(r'^getcurrentjuried/(?P<pk>[0-9]+)/$', views.GetCurrentDances, name='getcurrentjuried'),
]