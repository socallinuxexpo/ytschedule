from django.contrib import admin

from django.contrib import admin

from .models import Room
from .models import Talk
from .models import CommonDescription

admin.site.register(Room)
admin.site.register(Talk)
admin.site.register(CommonDescription)

