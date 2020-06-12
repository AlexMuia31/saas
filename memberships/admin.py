from django.contrib import admin
from . models import Client, Subscription, Membership


admin.site.register(Client)
admin.site.register(Subscription)
admin.site.register(Membership)
