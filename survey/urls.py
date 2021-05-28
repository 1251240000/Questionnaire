'''
Author: Hrlu
Date: 2021-04-26 21:17:11
LastEditors: Hrlu
LastEditTime: 2021-05-05 16:21:42
Description: hrlu.cn
'''
from django.urls import path, re_path

from survey import views

urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('index/', views.index),
    
    path('inventory', views.inventory),
    path('edit', views.edit),
    path('statistics', views.statistics),
    path('analysis', views.analysis),
    path('profile', views.profile),
    path('manage', views.manage),

    path('q/<str:sid>/', views.survey),
    re_path(r'.*', views.page_not_found),
]