# Generated by Django 2.1.1 on 2018-12-24 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ras_app', '0007_requestitem_additional_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=60)),
            ],
        ),
    ]
