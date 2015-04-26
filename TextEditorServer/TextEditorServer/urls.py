from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    url("", include("django_socketio.urls")),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
	url(r'^login/$', auth_views.login),
	url("", include("EditorApp.urls")),
)
