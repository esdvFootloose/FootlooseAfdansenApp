from django.conf.urls import url
from . import views

app_name = 'index'
urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.registerUser, name='register'),
    url(r'^about/$', views.about, name='about'),
    url(r'^clearcache/$', views.clearCache, name='clearcache'),
]