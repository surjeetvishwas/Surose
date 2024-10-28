# Generated by Django 5.0 on 2023-12-23 04:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_productorder_is_paid_productorder_is_shipped'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='first_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='last_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='phone',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='postcode',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='state',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productcart',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.productorder'),
        ),
    ]