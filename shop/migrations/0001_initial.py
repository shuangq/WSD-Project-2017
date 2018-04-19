# Generated by Django 2.0.1 on 2018-01-18 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shop.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(max_length=100)),
                ('link', models.URLField(blank=True, verbose_name='url')),
                ('price', models.FloatField(default=None)),
                ('description', models.TextField()),
                ('icon', models.ImageField(blank=True, null=True, upload_to=shop.models.Game.get_image_path)),
                ('difficulty', models.CharField(max_length=20)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GamesCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamesCategories', to='shop.Category')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamesCategories', to='shop.Game')),
            ],
            options={
                'verbose_name_plural': 'game categories',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_date', models.DateField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='shop.Game')),
                ('purchase_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=None)),
                ('date', models.DateField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='shop.Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.TextField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='shop.Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
