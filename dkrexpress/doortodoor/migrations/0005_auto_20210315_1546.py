# Generated by Django 3.1.7 on 2021-03-15 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doortodoor', '0004_article_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
