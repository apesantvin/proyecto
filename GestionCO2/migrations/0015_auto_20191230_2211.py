# Generated by Django 2.2.7 on 2019-12-30 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCO2', '0014_experto_id_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experto',
            name='id_usuario',
            field=models.IntegerField(default=0, unique=True),
        ),
    ]
