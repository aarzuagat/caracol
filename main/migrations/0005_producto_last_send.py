# Generated by Django 4.1.4 on 2022-12-31 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_producto_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='last_send',
            field=models.DateTimeField(null=True),
        ),
    ]