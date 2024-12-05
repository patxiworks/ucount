# Generated by Django 5.0.3 on 2024-11-26 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0018_alter_userplaceholders_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userplaceholders',
            name='tempid',
            field=models.IntegerField(blank=True, db_column='TempID', null=True),
        ),
        migrations.AlterField(
            model_name='userplaceholders',
            name='surname',
            field=models.CharField(blank=True, db_column='Surname', max_length=30, null=True, verbose_name='Surname'),
        ),
    ]
