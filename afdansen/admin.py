from django.contrib import admin
from .models import *

admin.site.register(Person)
admin.site.register(Dance)
admin.site.register(Pair)
admin.site.register(SubDance)
admin.site.register(DanceSubDanceRelation)
admin.site.register(Grade)
admin.site.register(Heat)
admin.site.register(MissingBackNumber)