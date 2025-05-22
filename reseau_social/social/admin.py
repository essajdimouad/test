from django.contrib import admin
from .models import Profile, Publication, Commentaire, Like, Message

admin.site.register(Profile)
admin.site.register(Publication)
admin.site.register(Commentaire)
admin.site.register(Like)
admin.site.register(Message)
