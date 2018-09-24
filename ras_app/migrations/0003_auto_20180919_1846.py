# Generated by Django 2.1.1 on 2018-09-19 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ras_app', '0002_auto_20180919_1752'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestor', models.EmailField(max_length=254)),
                ('signed_off', models.BooleanField(default=False)),
                ('signed_off_on', models.DateField(null=True)),
                ('reason', models.CharField(max_length=60)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Approver')),
                ('services', models.ManyToManyField(to='ras_app.Services')),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='approver',
        ),
        migrations.RemoveField(
            model_name='user',
            name='services',
        ),
        migrations.AddField(
            model_name='user',
            name='request',
            field=models.ManyToManyField(to='ras_app.Request'),
        ),
    ]