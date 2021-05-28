'''
Author: Hrlu
Date: 2021-04-24 19:57:04
LastEditors: Please set LastEditors
LastEditTime: 2021-04-27 20:26:28
Description: hrlu.cn
'''
from django.contrib import admin
from survey.models import *

# Register your models here.
admin.site.register(SurveyUser)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Solution)