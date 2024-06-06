# Generated by Django 4.2.4 on 2024-06-06 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('savetodb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='abnb_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='abnb_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='signature_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stay_num_guests',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
