# Generated by Django 5.1.3 on 2024-11-30 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsimage',
            name='uploaded_at',
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='image',
            field=models.ImageField(blank=True, upload_to='upload_filepath'),
        ),
    ]
