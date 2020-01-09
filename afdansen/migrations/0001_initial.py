# Generated by Django 3.0.2 on 2020-01-09 22:34

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Jury', models.ManyToManyField(blank=True, related_name='jury', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MissingBackNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Number', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FirstName', models.CharField(max_length=255)),
                ('Prefix', models.CharField(blank=True, max_length=255, null=True)),
                ('LastName', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['LastName'],
            },
        ),
        migrations.CreateModel(
            name='SubDance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('dancesubdancerelation',),
            },
        ),
        migrations.CreateModel(
            name='Pair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BackNumber', models.IntegerField()),
                ('Dances', models.ManyToManyField(related_name='pairs', to='afdansen.Dance')),
                ('FollowingRole', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pairs_following', to='afdansen.Person')),
                ('LeadingRole', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pairs_leading', to='afdansen.Person')),
            ],
            options={
                'ordering': ['LeadingRole', 'FollowingRole'],
            },
        ),
        migrations.CreateModel(
            name='Heat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Number', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('Dance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='heats', to='afdansen.Dance')),
                ('Persons', models.ManyToManyField(blank=True, related_name='heats', to='afdansen.Pair')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Grade', models.DecimalField(decimal_places=1, max_digits=3)),
                ('Dance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='afdansen.Dance')),
                ('Jury', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to=settings.AUTH_USER_MODEL)),
                ('Pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='afdansen.Pair')),
                ('Person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='afdansen.Person')),
                ('SubDance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='afdansen.SubDance')),
            ],
        ),
        migrations.CreateModel(
            name='DanceSubDanceRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Order', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('Dance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='afdansen.Dance')),
                ('SubDance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='afdansen.SubDance')),
            ],
            options={
                'ordering': ('Order',),
            },
        ),
        migrations.AddField(
            model_name='dance',
            name='SubDances',
            field=models.ManyToManyField(related_name='dances', through='afdansen.DanceSubDanceRelation', to='afdansen.SubDance'),
        ),
    ]