# Generated by Django 5.0 on 2023-12-23 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_productorder_address_productorder_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='country',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productorder',
            name='payment',
            field=models.CharField(choices=[('paypal', 'PayPal')], max_length=255, null=True),
        ),
    ]
