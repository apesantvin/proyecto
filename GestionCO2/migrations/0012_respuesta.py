# Generated by Django 3.0rc1 on 2019-11-22 15:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('GestionCO2', '0011_mensaje'),
    ]

    operations = [
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(blank=True, default='', null=True)),
                ('fecha_publicacion_respuesta', models.DateTimeField(default=django.utils.timezone.now)),
                ('mensaje', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respuestas', to='GestionCO2.Mensaje')),
            ],
        ),
    ]
