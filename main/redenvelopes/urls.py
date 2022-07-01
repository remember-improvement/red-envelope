from django.urls.resolvers import URLPattern
from redenvelopes.models import Redenvelope
from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter
from django.urls import path
from redenvelopes.views import RedenvelopeViewSet

redenvelope_router = SimpleRouter()
redenvelope_router.register('',RedenvelopeViewSet, basename='red-envelope')
urlpatterns = [
   *redenvelope_router.urls
]


