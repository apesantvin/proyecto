# Generated by Django 3.0rc1 on 2019-11-18 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCO2', '0004_auto_20191118_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edificio',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GestionCO2.Empresa'),
        ),
    ]
