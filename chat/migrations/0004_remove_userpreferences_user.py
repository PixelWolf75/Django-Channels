# Generated by Django 4.1.1 on 2022-11-19 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_chat_room_alter_room_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreferences',
            name='user',
        ),
    ]
