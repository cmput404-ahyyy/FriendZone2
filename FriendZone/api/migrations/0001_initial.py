# Generated by Django 2.1.7 on 2019-03-10 00:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('author_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=30)),
                ('lastName', models.CharField(max_length=30)),
                ('userName', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
                ('hostName', models.URLField()),
                ('githubUrl', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment', models.TextField()),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=32)),
                ('comment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('published', models.DateTimeField(verbose_name='date published')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('accepted', models.BooleanField(default=False)),
                ('regected', models.BooleanField(default=False)),
                ('from_author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend_request_sent', to='api.Author')),
                ('to_author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend_request_recieved', to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('author1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend1', to='api.Author')),
                ('author2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friend2', to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('postid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('source', models.URLField(blank=True, null=True)),
                ('origin', models.URLField(blank=True, null=True)),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=32)),
                ('publicationDate', models.DateTimeField()),
                ('content', models.TextField()),
                ('title', models.CharField(max_length=50)),
                ('permission', models.CharField(choices=[('M', 'me'), ('L', 'permitted authors'), ('F', 'my friends'), ('FF', 'friends of friends'), ('FH', 'friends on my host'), ('P', 'public')], default='P', max_length=2)),
                ('permitted_authors', models.TextField(null=True)),
                ('unlisted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Author')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='postid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Post'),
        ),
    ]
