from django.contrib.auth.models import User
from django.db.models import Model, AutoField, DateTimeField, CharField, ForeignKey, CASCADE, SET_NULL, OneToOneRel, OneToOneField
from django.utils.timezone import now


class Room(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, default="Room")
    created = DateTimeField(default=now)


class UserFriend(Model):
    user = ForeignKey(User, on_delete=CASCADE, db_index=True, related_name="friends")
    # friend = ForeignKey(User, on_delete=CASCADE, related_name="friends")
    room = ForeignKey(Room, on_delete=SET_NULL, null=True, related_name="users")


class UserPreferences(Model):
    id = OneToOneField(User, on_delete=CASCADE, primary_key=True)
    last_accessed_room = ForeignKey(Room, on_delete=CASCADE, db_index=True, related_name="last_rooms")


class Chat(Model):
    id = AutoField(primary_key=True)
    created = DateTimeField(default=now)
    room = ForeignKey(Room, on_delete=CASCADE, db_index=True, related_name="chat_list")
    message = CharField(max_length=100)
    user = ForeignKey(User, on_delete=CASCADE, db_index=True)

    def __str__(self):
        return f"#{self.id} {self.message}"

    class Meta:
        db_table = "chat"
