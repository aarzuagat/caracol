# Generated by Django 4.1.4 on 2022-12-11 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]
