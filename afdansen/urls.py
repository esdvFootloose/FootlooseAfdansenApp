from django.conf.urls import url
from . import views

app_name = 'afdansen'
urlpatterns = [
    url(r'^person/$', views.PersonList, name='personlist'),
    url(r'^person/create/$', views.CreatePerson, name='personcreate'),
    url(r'^person/edit/(?P<pk>[0-9]+)/$', views.EditPerson, name='personedit'),
    url(r'^person/delete/(?P<pk>[0-9]+)/$', views.DeletePerson, name='persondelete'),
    url(r'^pair/$', views.PairList, name='pairlist'),
    url(r'^pair/create/$', views.CreatePair, name='paircreate'),
    url(r'^pair/edit/(?P<pk>[0-9]+)/$', views.EditPair, name='pairedit'),
    url(r'^pair/delete/(?P<pk>[0-9]+)/$', views.DeletePair, name='pairdelete'),
    url(r'^jury/create/$', views.CreateJury, name='createjury'),
    url(r'^jury/edit/$', views.EditJury, name='editjury'),
    url(r'^jury/dancepage/(?P<danceid>[0-9]+)/(?P<heatid>[0-9]+)/$', views.juryPageDance, name='jurypagedance'),
    url(r'^jury/dances/$', views.juryPage, name='jurypage'),
    url(r'^subdancerelation/create/$', views.CreateSubDanceRelation, name='createsubdancerelation'),
    url(r'^subdancerelation/delete/(?P<danceid>[0-9]+)/(?P<subdanceid>[0-9]+)/$', views.SubDanceRelationDelete, name='subdancerelationdelete'),
    url(r'^subdancerelation/up/(?P<danceid>[0-9]+)/(?P<subdanceid>[0-9]+)/$', views.SubDanceOrderUp, name='subdancerelationup'),
    url(r'^subdancerelation/down/(?P<danceid>[0-9]+)/(?P<subdanceid>[0-9]+)/$', views.SubDanceOrderDown, name='subdancerelationdown'),
    url(r'^dances/$', views.DanceList, name='dancelist'),
    url(r'^grades/$', views.GradeList, name='gradelist'),
    url(r'^import/$', views.ImportPairs, name='import'),
    url(r'^results/$', views.ResultList, name='resultlist'),
    url(r'^heat/create/$', views.CreateHeat, name='createheat'),
    url(r'^heat/edit/(?P<pk>[0-9]+)/$', views.EditHeat, name='editheat'),
    url(r'^heat/edit/$', views.EditHeatList, name='editheatlist'),
    url(r'^heat/list/$', views.HeatListAll, name='heatlistall'),
    url(r'^heat/editlist/(?P<pk>[0-9]+)/$', views.HeatEditListDance, name='heateditlistdance'),
    url(r'^heat/dancelist/$', views.HeatDanceChooseList, name='heatdancechooselist'),
    url(r'^livestream/$', views.LiveStream, name='livestreamer'),
    url(r'^print/heatlist/$', views.PrintHeatList, name='printheatlist'),
    url(r'^jury/formprint/(?P<danceid>[0-9]+)/(?P<heatid>[0-9]+)/$', views.PrintJuryForm, name='printjuryform'),
    url(r'^pair/recalcbacknumbers/$', views.RecalcBackNumbers, name='recalcbacknumbers'),
]