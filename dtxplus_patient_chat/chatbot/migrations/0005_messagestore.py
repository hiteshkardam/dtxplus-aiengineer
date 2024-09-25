# Generated by Django 5.1 on 2024-09-25 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0004_delete_messagestore'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField()),
                ('message', models.JSONField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'message_store',
                'managed': False,
            },
        ),
    ]
