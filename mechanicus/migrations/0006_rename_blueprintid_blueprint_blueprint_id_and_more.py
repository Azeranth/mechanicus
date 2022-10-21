# Generated by Django 4.0.8 on 2022-10-18 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mechanicus', '0005_alter_job_assignee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blueprint',
            old_name='blueprintId',
            new_name='blueprint_id',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='itemId',
            new_name='item_id',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='product',
            new_name='blueprint',
        ),
        migrations.RenameField(
            model_name='skill',
            old_name='skillId',
            new_name='skill_id',
        ),
        migrations.AddField(
            model_name='job',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]