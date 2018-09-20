# Generated by Django 2.1.1 on 2018-09-19 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Approverlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Servicelist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Userlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=254)),
                ('end_date', models.DateField(default=True)),
                ('approver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ras_app.Approverlist')),
                ('services_approved', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ras_app.Servicelist')),
            ],
        ),
    ]
