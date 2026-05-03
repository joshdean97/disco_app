from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("disco_app", "0002_alter_shift_options_remove_shift_worker_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="latitude",
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="site",
            name="longitude",
            field=models.FloatField(null=True, blank=True),
        ),
    ]
