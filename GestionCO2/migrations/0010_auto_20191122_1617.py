# Generated by Django 3.0rc1 on 2019-11-22 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCO2', '0009_consumo_edificioconsumo_vehiculoconsumo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edificioconsumo',
            name='tipo',
            field=models.CharField(choices=[('1', 'Agua'), ('2', 'Electricidad'), ('3', 'Aceite'), ('4', 'Propano'), ('5', 'Gas Natural')], max_length=50, verbose_name='¿Que ha consumido?'),
        ),
        migrations.AlterField(
            model_name='vehiculoconsumo',
            name='tipo',
            field=models.CharField(choices=[('1', 'Electricidad'), ('2', 'Gasolina'), ('3', 'Diesel')], max_length=50, verbose_name='¿Que ha consumido?'),
        ),
    ]
