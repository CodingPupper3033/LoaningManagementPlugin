# Generated by Django 3.2.19 on 2023-11-15 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanmanagement', '0007_auto_20231113_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loansession',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='loanuser',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]