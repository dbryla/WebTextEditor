from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
	url(r'^createUser/$', views.createUser, name='createUser'),
	url(r'^logout/$', views.logoutUser, name='logout'),
)
