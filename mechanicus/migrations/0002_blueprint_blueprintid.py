# Generated by Django 4.0.8 on 2022-10-15 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mechanicus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blueprint',
            name='blueprintId',
            field=models.IntegerField(default='-1'),
            preserve_default=False,
        ),
    ]
