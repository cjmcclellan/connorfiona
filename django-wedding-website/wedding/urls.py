from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url('RSVP', views.RSVP, name='RSVP'),
    url('rsvp', views.RSVP, name='rsvp')
]
