# Generated by Django 2.1.1 on 2018-10-12 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ras_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestitem',
            name='services',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Services'),
        ),
    ]