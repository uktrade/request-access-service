# Generated by Django 2.1.1 on 2019-07-24 11:07

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountsCreator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(blank=True, max_length=60)),
                ('email', models.EmailField(max_length=254)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Approver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestor', models.EmailField(max_length=254)),
                ('signed_off', models.BooleanField(default=False)),
                ('signed_off_on', models.DateTimeField(null=True)),
                ('reason', models.CharField(default=False, max_length=400)),
                ('user_email', models.EmailField(max_length=254)),
                ('token', models.CharField(default=False, max_length=20)),
                ('completed', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
                ('rejected_reason', models.CharField(blank=True, max_length=400)),
                ('approver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Approver')),
            ],
        ),
        migrations.CreateModel(
            name='RequestItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('additional_info', models.CharField(blank=True, max_length=60)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Request')),
            ],
        ),
        migrations.CreateModel(
            name='RequestorDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=60)),
                ('service_url', models.URLField(blank=True)),
                ('service_docs', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(max_length=60)),
                ('sc', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=60)),
                ('surname', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=60)),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ras_app.Request')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Teams')),
            ],
        ),
        migrations.AddField(
            model_name='requestitem',
            name='services',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ras_app.Services'),
        ),
        migrations.AddField(
            model_name='accountscreator',
            name='services',
            field=models.ManyToManyField(to='ras_app.Services'),
        ),
    ]
