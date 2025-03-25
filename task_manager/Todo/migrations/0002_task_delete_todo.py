# Generated by Django 4.2.5 on 2025-02-15 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Todo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=254)),
                ('completed', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'ToDo',
            },
        ),
        migrations.DeleteModel(
            name='ToDo',
        ),
    ]
