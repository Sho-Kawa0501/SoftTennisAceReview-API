# Generated by Django 4.2.7 on 2023-12-01 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='image',
            field=models.ImageField(default='profile/default.png', upload_to='profiles'),
        ),
    ]
