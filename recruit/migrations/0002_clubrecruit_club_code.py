# Generated by Django 5.1.3 on 2024-12-03 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubrecruit',
            name='club_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]