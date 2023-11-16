# Generated by Django 3.2.19 on 2023-11-16 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanmanagement', '0009_alter_loanuser_idn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loanuser',
            name='email',
            field=models.EmailField(default=None, max_length=20, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='loanuser',
            name='first_name',
            field=models.CharField(default=None, max_length=250, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='loanuser',
            name='last_name',
            field=models.CharField(default=None, max_length=250, verbose_name='Name'),
        ),
    ]
