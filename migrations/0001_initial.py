# Generated by Django 3.2.19 on 2023-09-28 20:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stock', '0102_alter_stockitem_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoanUser',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Id')),
                ('first_name', models.CharField(max_length=250, verbose_name='Name')),
                ('last_name', models.CharField(max_length=250, verbose_name='Name')),
                ('email', models.EmailField(max_length=20, verbose_name='Email')),
                ('idn', models.IntegerField(verbose_name='RIN')),
                ('active', models.BooleanField(verbose_name='Active')),
                ('restricted', models.BooleanField(verbose_name='Restricted')),
            ],
        ),
        migrations.CreateModel(
            name='LoanSession',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='Id')),
                ('quantity', models.DecimalField(decimal_places=5, default=1, max_digits=15, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Stock Quantity')),
                ('loan_date', models.DateField(verbose_name='Date Loaned')),
                ('due_date', models.DateField(verbose_name='Due Date')),
                ('returned', models.BooleanField(default=False, verbose_name='Returned')),
                ('date_returned', models.DateField(blank=True, null=True, verbose_name='Due Date')),
                ('stock_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.stockitem')),
            ],
        ),
    ]
