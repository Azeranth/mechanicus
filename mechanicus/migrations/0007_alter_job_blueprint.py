# Generated by Django 4.0.8 on 2022-10-19 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mechanicus', '0006_rename_blueprintid_blueprint_blueprint_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='blueprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='mechanicus.blueprint'),
        ),
    ]
