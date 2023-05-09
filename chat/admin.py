from django.contrib import admin

from chat.models import *


class ChatAdmin(admin.ModelAdmin):
    list_display = ['created', 'room', 'message', 'user']


class RoomAdmin(admin.ModelAdmin):
    list_display = ['created', 'name']


class UserFriendAdmin(admin.ModelAdmin):
    list_display = ['user', 'room']

class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_accessed_room']


admin.site.register(Chat, ChatAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(UserFriend, UserFriendAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)

