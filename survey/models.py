'''
Author: Hrlu
Date: 2021-04-24 19:33:46
LastEditors: Please set LastEditors
LastEditTime: 2021-05-01 22:50:18
Description: hrlu.cn
'''
from django.db import models
from django.contrib.auth.models import User

from survey.utils import Base62
# Create your models here.

class SurveyUser(models.Model):
    '''
    拓展 User 模型以拓展用户属性
    '''
    ROLES = (
        ('user', "用户"),
        ('superuser', "超级用户"),
        ('admin', "管理员"),
    )

    user = models.OneToOneField(
        User, 
        primary_key=True, 
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        "角色",
        max_length=16,
        choices=ROLES,
    )
    prompt = models.CharField(
        "提示问题",
        max_length=128,
    )
    reply = models.CharField(
        "提示问题答案",
        max_length=128,
    )


class Survey(models.Model):
    '''
    问卷集
    由超级用户创建的问卷，创建时会生成7位唯一随机码用于主键。
    创建时可自定义问卷名称、描述，并选择是否公开，及是否允许
    用户再次问卷以修改答案。
    '''
    id = models.CharField(
        "问卷码",
        max_length=7,
        unique=True,
        primary_key=True,
        editable=False,
        default=Base62.BaseID,
    )
    founder = models.ForeignKey(
        SurveyUser,
        on_delete=models.CASCADE,
        related_name='surveys',
    )
    creation_time = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
    )
    title = models.CharField(
        "问卷名称",
        max_length=32,
    )
    description = models.TextField(
        "问卷描述",
    )
    public = models.BooleanField(
        "是否公开",
        default=True,
    )
    modifiable = models.BooleanField(
        "是否允许提交后修改",
        default=True,
    )
    activate = models.BooleanField(
        "是否激活",
        default=True,
    )

class Question(models.Model):
    '''
    问题集
    用户创建问卷时可提交多个问题，与问卷集相似的创建问题码。
    创建由用户选择题目类型及答案类型，并输入相应题目及答案，
    备选答案需在答案类型为选择题或多选题时使用。
    '''
    TOPIC_TYPES = (
        ('text', "文本"),
        ('richtext', "富文本"),
        ('markdown', "Markdown"),
    )
    ANSWER_TYPES = (
        ('select', "选择题"),
        ('checkbox', "多选题"),
        ('input', "填空题"),
        ('textbox', "简答题"),
    )
    id = models.CharField(
        "问题码",
        max_length=7,
        unique=True,
        primary_key=True,
        editable=False,
        default=Base62.BaseID,
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    order = models.IntegerField(
        "题目序号",
        default=0,
    )
    topic_type = models.CharField(
        "题目类型",
        max_length=16,
        choices=TOPIC_TYPES,
    )
    topic = models.TextField(
        "题目",
    )
    answer_type = models.CharField(
        "答案类型",
        max_length=16,
        choices=ANSWER_TYPES,
    )
    answers = models.JSONField(
        "备选答案",
        default=list,
    )
    blank = models.BooleanField(
        "是否允许为空",
        default=True,
    )

class Solution(models.Model):
    '''
    解答集
    用户提交问卷后生成解答集，若问卷属性为公开，则该问卷的解
    答集将允许解答人为空、若问卷属性为允许修改，则该问卷的解
    答集将允许用户多次提交问卷以修改此解答集。
    '''
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='solutions',
    )
    surveyuser = models.ForeignKey(
        SurveyUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='solutions',
    )
    anonymous = models.CharField(
        "匿名用户",
        max_length=16,
        null=True,
        blank=True,
    )
    answer = models.CharField(
        "解答内容",
        max_length=1024,
    )
    submission_time = models.DateTimeField(
        "提交时间",
        auto_now_add=True,
    )