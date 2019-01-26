from django.conf.urls import url, include

from . import views
from tastypie.api import Api
from .api import RoomResource, StreamResource

v1_api = Api(api_name='v1')
v1_api.register(RoomResource())
v1_api.register(StreamResource())

urlpatterns = [
    # ex: /
    url(r'^$', views.index, name='index'),
    url(r'^api/',  include(v1_api.urls)),
]
