# Generated by Django 3.2.16 on 2023-03-13 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_review_ticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='ticket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ticket'),
        ),
    ]
