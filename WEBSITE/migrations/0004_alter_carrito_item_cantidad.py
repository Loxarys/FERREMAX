# Generated by Django 5.0.7 on 2024-07-10 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WEBSITE', '0003_direccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrito_item',
            name='cantidad',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
