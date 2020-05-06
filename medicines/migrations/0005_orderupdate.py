# Generated by Django 2.1.5 on 2020-05-05 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicines', '0004_auto_20200505_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderUpdate',
            fields=[
                ('update_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_id', models.IntegerField(default='')),
                ('update_desc', models.CharField(default='', max_length=5000)),
                ('timestamp', models.DateField(auto_now_add=True)),
            ],
        ),
    ]