'''
Author: Hrlu
Date: 2021-04-26 20:35:21
LastEditors: Hrlu
LastEditTime: 2021-04-26 21:20:44
Description: hrlu.cn
'''

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('survey.urls')),
]

handler404 = "survey.views.page_not_found"
handler500 = "survey.views.internal_server_error"