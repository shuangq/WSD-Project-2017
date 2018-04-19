# Generated by Django 2.0.2 on 2018-02-11 16:02

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='game_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='external_files/game_icons', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['bmp', 'bufr', 'cur', 'pcx', 'dcx', 'dds', 'ps', 'eps', 'fit', 'fits', 'fli', 'flc', 'ftc', 'ftu', 'gbr', 'gif', 'grib', 'h5', 'hdf', 'png', 'jp2', 'j2k', 'jpc', 'jpf', 'jpx', 'j2c', 'icns', 'ico', 'im', 'iim', 'tif', 'tiff', 'jfif', 'jpe', 'jpg', 'jpeg', 'mpg', 'mpeg', 'mpo', 'msp', 'palm', 'pcd', 'pdf', 'pxr', 'pbm', 'pgm', 'ppm', 'psd', 'bw', 'rgb', 'rgba', 'sgi', 'ras', 'tga', 'webp', 'wmf', 'emf', 'xbm', 'xpm'])]),
        ),
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.FloatField(default=None, validators=[django.core.validators.DecimalValidator(10, 2)]),
        ),
        migrations.AlterField(
            model_name='score',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterUniqueTogether(
            name='gamescategory',
            unique_together={('game', 'category')},
        ),
        migrations.AlterUniqueTogether(
            name='purchase',
            unique_together={('purchase_user', 'game')},
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together={('user', 'game')},
        ),
    ]
