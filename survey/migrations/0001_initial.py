# Generated by Django 3.1.4 on 2021-04-24 13:35

from django.db import migrations, models
import django.db.models.deletion
import survey.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.CharField(default=survey.utils.Base62.BaseID, editable=False, max_length=7, primary_key=True, serialize=False, unique=True, verbose_name='问题码')),
                ('topic_type', models.CharField(choices=[('text', '文本'), ('richtext', '富文本'), ('markdown', 'Markdown')], max_length=16, verbose_name='题目类型')),
                ('topic', models.TextField(verbose_name='题目')),
                ('answer_type', models.CharField(choices=[('select', '选择题'), ('checkbox', '多选题'), ('input', '填空题'), ('textbox', '简答题')], max_length=16, verbose_name='答案类型')),
                ('answers', models.JSONField(default=list, verbose_name='备选答案')),
            ],
        ),
        migrations.CreateModel(
            name='SurveyUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('role', models.CharField(choices=[('user', '用户'), ('superuser', '超级用户'), ('admin', '管理员')], max_length=16, verbose_name='角色')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.CharField(default=survey.utils.Base62.BaseID, editable=False, max_length=7, primary_key=True, serialize=False, unique=True, verbose_name='问卷码')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('title', models.CharField(max_length=32, verbose_name='问卷名称')),
                ('description', models.CharField(max_length=256, verbose_name='问卷描述')),
                ('public', models.BooleanField(default=True, verbose_name='是否公开')),
                ('modify', models.BooleanField(default=True, verbose_name='是否允许提交后修改')),
                ('activate', models.BooleanField(default=True, verbose_name='是否激活')),
                ('founder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='survey.surveyuser')),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=1024, verbose_name='解答内容')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='survey.question')),
                ('surveyuser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='solutions', to='survey.surveyuser')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='survey.survey'),
        ),
    ]
