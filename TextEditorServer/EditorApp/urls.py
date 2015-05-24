from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^createUser/$', views.createUser, name='createUser'),
	url(r'^logout/$', views.logoutUser, name='logout'),
	url(r'^upload/$', views.upload, name='upload'),
	url(r'^download/$', views.download, name='download'),
)
