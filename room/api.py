from tastypie.resources import Resource, ModelResource, Bundle
from tastypie.cache import SimpleCache
from tastypie import fields
from .models import Room, YouTube

class RoomResource(ModelResource):
  class Meta:
    queryset = Room.objects.all()
    resource_name = 'room'
    allowed_methods = ['get']
    always_return_data = True
    filtering = {
      'is_streaming': ['exact'],
      'state': ['exact'],
      'start_time': ["exact", "lt", "lte", "gte", "gt"],
      'end_time': ["exact", "lt", "lte", "gte", "gt"],
    }
    excludes = ['ingestion_address', 'backup_address']

class Stream():
  def __init__(self, dictionary):
    for key in dictionary:
      setattr(self, key, dictionary[key])


class StreamResource(Resource):
    name = fields.CharField(attribute='name')
    status = fields.CharField(attribute='status')
    health = fields.CharField(attribute='health')

    class Meta:
      resource_name = 'stream'
      allowed_methods = ['get']
      always_return_data = True
      limit = 50
      cache = SimpleCache(timeout=60)

    def detail_uri_kwargs(self, bundle_or_obj):
      kwargs = {}
      if isinstance(bundle_or_obj, Bundle):
        kwargs['pk'] = bundle_or_obj.obj.name
      else:
        kwargs['pk'] = bundle_or_obj.name

      return kwargs

    def get_object_list(self, request):
        results = []
        streams = YouTube.list_stream_health()
        
        for result in streams:
          results.append(Stream(result) )
        return results

    def obj_get_list(self, bundle, **kwargs):
      return self.get_object_list(bundle.request)


