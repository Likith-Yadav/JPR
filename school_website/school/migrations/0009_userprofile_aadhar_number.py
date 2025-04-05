# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0008_userprofile_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='aadhar_number',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True),
        ),
    ] 