# Generated by Django 4.1.1 on 2023-09-06 06:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_usercurrency'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currencyrate',
            options={'ordering': ['-id']},
        ),
    ]