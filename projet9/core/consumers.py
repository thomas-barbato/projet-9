from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import render, redirect, HttpResponseRedirect
from channels.auth import login as channels_login
from .forms import *
from .models import *
import json
from django.contrib.sessions.models import Session


class LoginConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        print("dans connect")
        self.accept()

    async def send(self):
        print("ok")

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        if "username" in data:
            print(data["username"])
        text_data_json = json.loads(text_data)
        print(text_data_json)
        username = text_data_json["username"]
        password = text_data_json["password"]
        if User.objects.filter(
            username__iexact=username, password__iexact=password
        ).exists():
            user = await User.objects.get(
                username__iexact=username, password__iexact=password
            )
            await channels_login(self.scope, user)
            # save the session (if the session backend does not access the db you can use `sync_to_async`)
            await database_sync_to_async(self.scope["session"].save)()
