# Generated by Django 4.2.15 on 2025-01-22 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventree_loan', '0003_loansession_loaner'),
    ]

    operations = [
        migrations.AddField(
            model_name='loansession',
            name='last_notice',
            field=models.DateField(blank=True, null=True, verbose_name='Last Overdue Notice Send Date'),
        ),
        migrations.AddField(
            model_name='loansession',
            name='notices_sent',
            field=models.IntegerField(default=0),
        ),
    ]
