# Generated by Django 2.1.1 on 2018-09-30 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ras_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ras_app.Request'),
        ),
    ]
