# chat/views.py
import json
from itertools import groupby
from time import sleep

from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from chat.models import *

client_user: str


def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    # Room should be access byy ID not name as it isn't unique
    room_current = Room.objects.filter(name=room_name).first()
    if room_current is None:
        room_current = Room.objects.create(name=room_name)

    user = User.objects.filter(username=client_user.lower()).first()

    user_client = UserFriend.objects.filter(user=user)
    if user_client.first() is None:
        pass

    chat_list: list[dict] = [{
        'id': c.id,
        'created': c.created.isoformat(),
        'message': c.message,
    } for c in list(Chat.objects.filter(room=room_current).all())]

    return render(request, 'chat/room.html', {
        # 'room_name': room_name,
        'history': chat_list,
        'user_id': user.id
    })


class LoginPage(TemplateView):
    template_name = "chat/login.html"

    def post(self, request: HttpRequest):
        # Advance checking of username with database here
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        user = User.objects.filter(username=username.lower()).first()
        if user is None:
            return render(request, LoginPage.template_name, {
                "error": "Bad Login incorrect username"
            })

        if not check_password(password, user.password):
            return render(request, LoginPage.template_name, {
                "error": "Bad Login incorrect password"
            })

        login(request, user)
        return HttpResponseRedirect(redirect_to=reverse('home'))


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = "chat/home2.html"

    def get(self, request: HttpRequest):
        return render(request, self.__class__.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        current_user = self.request.user

        friend_list: list[UserFriend] = self.request.user.friends.all() if isinstance(self.request.user, User) else []

        room_list: list[Room] = [f.room for f in friend_list]
        all_uf: list[UserFriend] = UserFriend.objects.filter(room__in=room_list).exclude(user=current_user).order_by('room').all()

        rooms_map: dict[Room, list[UserFriend]] = {k: list(list_v) for k, list_v in
                                                   groupby(all_uf, key=lambda x: x.room)}
        # room_map: dict[int, Room] = {r.id: r for r in room_list}
        for r in room_list:
            setattr(r, 'chats', list(r.chat_list.order_by('created').all()))
            if len(rooms_map[r]) == 1:
                # Name the room of the other guy
                r.name = rooms_map[r][0].user.username

            attendant_list = ",".join([u.user.username for u in rooms_map[r]]) if len(rooms_map[r]) > 1 else \
            rooms_map[r][0].user.username
            setattr(r, 'attendant_list', attendant_list)

        json_room_list = [{
            'id': r.id,
            'name': r.name,
            'created': r.created.isoformat(),
            'attendant_list': getattr(r, 'attendant_list'),
            'chat_list': [{
                'id': c.id,
                'created': c.created.isoformat(),
                'message': c.message,
                'user_id': c.user_id
            } for c in list(r.chat_list.order_by('created').all())]
        } for r in room_list]

        # all_uf: list[UserFriend] = UserFriend.objects.filter(room__in=room_list).exclude(user=current_user).order_by('room').all()
        # rooms_map: dict[Room, list[User]] = {k: list(list_v) for k, list_v in groupby(all_uf, key=lambda x: x.room)}
        room_history_list: dict[int, list[dict]] = {}
        # create defaults
        for r in room_list:
            room_history_list[r.id] = []

        for c in list(Chat.objects.all()):
            room_history_list.setdefault(c.room_id, [])
            room_history_list[c.room_id].append({
                "id": c.id,
                "message": c.message,
                "created": c.created
            })

        current_preference = UserPreferences.objects.filter(id=current_user)
        # TODO: Move this to the login section
        if current_preference.count() == 0:
            UserPreferences.objects.create(id=current_user, last_accessed_room=all_uf[0].room)

        return {
            'user_id': self.request.user.id,
            'user_name': self.request.user.username,
            'last_room_accessed': current_preference.first().last_accessed_room_id,
            # 'rooms_map': rooms_map,
            'histories': room_history_list,
            'room_list': json_room_list,
        }
#
#
# class LoginPage(TemplateView):
#     template_name = "chat/login.html"
#
#     def post(self, request: HttpRequest):
#         try:
#             User.objects.get(username=request.username, password=request.password)
#         except:
#             return render
#         return JsonResponse({})
