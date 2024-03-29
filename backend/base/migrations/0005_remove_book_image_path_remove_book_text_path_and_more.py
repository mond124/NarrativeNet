# Generated by Django 5.0.1 on 2024-02-14 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_book_image_path_alter_book_text_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='image_path',
        ),
        migrations.RemoveField(
            model_name='book',
            name='text_path',
        ),
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(default='default_cover.jpg', upload_to='covers/'),
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='chapters/')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.book')),
            ],
        ),
    ]
