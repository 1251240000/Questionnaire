'''
Author: Hrlu
Date: 2021-05-04 23:40:27
LastEditors: Hrlu
LastEditTime: 2021-05-05 18:02:40
Description: hrlu.cn
'''
import re
import datetime
from collections import Counter

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F

from survey.models import *
from survey.utils import *

def login(request):
    if request.method == 'POST':
        # 从POST请求中获取用户名、密码
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_path = request.GET.get("next", "/")
        
        if not username or not password:
            code, msg = 201, "用户名或密码不能为空！"
        else:
            user = auth.authenticate(
                request,
                username=username, 
                password=password
            )
            # 若用户验证成功，则重定向至来源地址
            # 若用户验证失败，返回提示信息 
            if user is not None:
                auth.login(request, user)
                return redirect(next_path)
            else:
                code, msg = 202, "用户名或密码错误！"
        return render(request, 'login.html', {'code': code, 'msg': msg})
    elif request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        return redirect('/login/')

@login_required
def logout(request):
    auth.logout(request, )
    return redirect('/login/')
 
def register(request):
    if request.method == 'POST':
        # 从POST请求中获取用户名、密码、密码校验
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmed = request.POST.get('confirmed')
        # 验证输入合法性
        if not username or not password:
            code, msg = 201, "用户名或密码不能为空！"
        elif password != confirmed:
            code, msg = 202, "密码输入不一致！"
        elif User.objects.filter(username = username).exists():
            code, msg = 203, "该用户已存在！"
        else:
            # 先创建基础用户，再绑定并创建问卷系统用户
            user = User.objects.create_user(
                username = username,
                password = password,
            )
            SurveyUser.objects.create(
                user = user,
                role = 'user',
            )
            code, msg = 200, "创建成功！"
        return render(request, 'register.html', {'code': code, 'msg': msg})
        
    elif request.method == 'GET':
        return render(request, 'register.html', {})
    else:
        return redirect('/login/')

@login_required
def index(request):
    if request.method == 'GET':
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        if user.user.first_name:
            user_name = user.user.first_name
        resp_data = {
            'user': user_name,
            'is_superuser': user.user.is_superuser,
        }
        return render(request, 'index.html', resp_data)
    if request.method == 'POST':
        username = request.user
        password = request.POST.get('password')
        user = auth.authenticate(
            request,
            username=username, 
            password=password
        )
        if user is None:
            return JsonResponse({'code': 401, 'msg': "请输入正确的密码！"})
        new = request.POST.get('new')
        confirmed = request.POST.get('confirmed')
        if new != confirmed:
            return JsonResponse({'code': 402, 'msg': '两次输入的密码不一致！'})
        user.set_password(new)
        user.save()
        auth.login(request, user)
        return JsonResponse({'code': 200, 'msg': "修改成功！"})

    else:
        return page_not_found(request, )

@login_required
def profile(request):
    if request.method == 'GET':
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        resp_data = {
            'username': user.user.username,
            'first_name': user.user.first_name,
            'email': user.user.email,
            'is_superuser': user.user.is_superuser,
            'role': user.role,
            'prompt': user.prompt,
            'reply': user.reply,
        }
        return render(request, 'profile.html', resp_data)
    elif request.method == 'POST':
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        user.user.first_name = request.POST.get('first_name', '')
        user.user.email = request.POST.get('email', '')
        user.prompt = request.POST.get('prompt', '')
        user.reply = request.POST.get('reply', '')
        user.user.save()
        user.save()
        return redirect('/profile')
    return page_not_found(request)

@login_required
def manage(request):
    if request.method == 'GET':
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        if not user.user.is_superuser:
            return page_not_found(request)
        resp_data = {
            'users': SurveyUser.objects.values(
                'user_id', 'role', 'user__date_joined', 'user__username', 
                'user__is_active', 'user__first_name', 
                'user__email', 'user__is_superuser',
            )
        }
        return render(request, 'manage.html', resp_data)
    elif request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = SurveyUser.objects.get(user_id = user_id)
        is_active = request.POST.get('is_active')
        password = request.POST.get('password')
        if is_active:
            user.user.is_active = is_active == 'true'
        if password:
            user.user.set_password(password)
        user.user.save()
        if password and user.user.username == request.user:
            auth.login(request, user.user)
        return JsonResponse({'code': 200, 'msg':"修改成功！"})

    return page_not_found(request)

def survey(request, sid = None):
    # 渲染问卷， SID为问卷ID
    if request.method == 'GET':
        # 判断问卷是否存在，若不存在则返回404
        if sid is None:
            return page_not_found(request)
        elif not Survey.objects.filter(id = sid).exists():
            return page_not_found(request)

        try:
            # 获取问卷及题目的各项属性值
            survey = Survey.objects.get(id = sid)
            questions = Question.objects.filter(survey = survey).values(
                'id', 'order', 'topic_type', 'topic', 'answer_type', 'answers', 'blank'
            ).order_by('order')
            if not survey.activate:
                resp = {
                    'title': "问卷调查已结束",
                    'desc': "您可以进入主页查看其它问卷，或发布您的问卷调查",
                }
                return render(request, 'submitted.html', resp)
            
            # 校验问卷是否需要权限验证及是否已提交过
            if not survey.public and not request.user.is_authenticated:
                return redirect(r'/login/?next=/q/%s/'%sid)
            elif not request.user.is_authenticated:
                # 匿名用户生成16位身份码
                agent = request.environ.get('HTTP_USER_AGENT')
                anonymous = make_sha16(agent)
                
                submitted = Solution.objects.filter(
                    question__survey = survey,
                    anonymous = anonymous,
                ).exists()
            else:
                # 获取当前登录的用户
                user_name = request.user
                user = SurveyUser.objects.get(user__username = user_name)

                submitted = Solution.objects.filter(
                    question__survey = survey,
                    surveyuser = user,
                ).exists()
            
            # 序列化渲染数据
            resp = {
                'survey_title': survey.title,
                'survey_desp': survey.description,
                'survey_modifiable': survey.modifiable,
                'submitted': submitted,
                'questions': questions,
            }
            
            return render(request, 'survey.html', resp)

        except Exception as e:
            return internal_server_error(request, e)
    
    # 处理提交的问卷调查
    elif request.method == 'POST':
        # 获取所有的问题ID
        qid_list = [k for k in request.POST.keys() if re.match(r'^.{7}$', k)]
        q_queryset = Question.objects.filter(id__in = qid_list)
        # 获取问卷对象
        survey = q_queryset.values_list('survey', flat=True).distinct()
        
        if survey.count() != 1:
            return internal_server_error(request, )

        survey = survey.first()

        # 验证问卷权限限制
        if not request.user.is_authenticated:
            # 生成匿名用户指纹
            agent = request.environ.get('HTTP_USER_AGENT')
            anonymous = make_sha16(agent)
            user = None
        else:
            user_name = request.user
            user = SurveyUser.objects.get(user__username = user_name)
            anonymous = ''

        q_types = dict(q_queryset.values_list('id', 'answer_type'))

        try:
            for qid in qid_list:
                if q_types.get(qid, ) == 'checkbox':
                    ans = request.POST.getlist(qid, [])
                elif q_types.get(qid, ) in ('select', 'input', 'textbox'):
                    ans = request.POST.get(qid, '')
                else:
                    continue
                # 更新或提交问题解答
                Solution.objects.update_or_create(
                    question = Question.objects.get(id = qid),
                    surveyuser = user,
                    anonymous = anonymous,
                    defaults = {
                        'answer': ans,
                    }
                )
        except Exception as e:
            return internal_server_error(request, exception = e)

        # 返回提交后界面
        resp = {
            'title': "感谢您的参与",
            'desc': "您可以进入主页查看您的提交，或发布您的问卷调查",
        }
        return render(request, 'submitted.html', resp)

    return redirect('/')

@login_required
def inventory(request):
    # 问卷清单界面
    if request.method == 'GET':
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        # home代表我的问卷、 market代表问卷市场
        page = request.GET.get('page', 'home')
        # 获取查询集，及界面中需要显示的页面元素
        fieldset = [
                'activate', 'title', 'creation_time', 
                'questions_count', 'surveyuser_count', 
                'public', 'annoymous_count', 'modifiable', 
                'options', 'edit', 'setting', 'delete', 'founder'
            ]
        # 我的问卷视图
        if page == 'home':
            queryset = Survey.objects.filter(founder = user,).order_by('-creation_time')
            fields = [f for f in fieldset if f not in ('founder', )]
        # 管理员问卷市场
        elif user.user.is_superuser:
            queryset = Survey.objects.order_by('-creation_time')
            fields = fieldset
        # 普通用户问卷市场
        else:
            queryset = Survey.objects.filter(activate = True, public = True)
            fields = [
                'title', 'founder', 'questions_count', 
                'surveyuser_count', 'modifiable', 'options',
            ]

        # 搜索功能实现
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(title__contains = search)
        
        # 序列化渲染所需数据、包含问卷列表及其各项属性，同时需汇总出问题数量、提交用户数量、匿名提交数量
        resp = {
            'page': page,
            'fields': fields,
            'survey_list': queryset.values(
                'id', 
                'creation_time',
                'founder__user__username',
                'title',
                'description',
                'public',
                'modifiable',
                'activate',
            ).annotate(
                questions_count = Count(
                    'questions', 
                    distinct=True,
                ),
                surveyuser_count = Count(
                    'questions__solutions__surveyuser', 
                    distinct=True,
                ),
                anonymous_count = Count(
                    'questions__solutions__anonymous', 
                    distinct=True,
                    filter=~Q(questions__solutions__anonymous = ''),
                ),
            )
        }
        return render(request, 'inventory.html', resp)
    # ToolBar功能实现
    elif request.method == 'POST':
        req_type = request.POST.get('type', '')
        # 问卷删除功能
        if req_type == 'delete':
            survey_id = request.POST.get('survey', '')
            survey = Survey.objects.get(id = survey_id)
            survey.delete()
        return redirect('/inventory?page=home')
    
    return page_not_found(request)

@login_required
def edit(request):
    # 问卷/问题编辑器界面渲染
    if request.method == 'GET':
        survey_id = request.GET.get('survey', '')
        content = request.GET.get('content', '')
        # 若问卷存在则返回问卷信息，否则返回空问卷
        if Survey.objects.filter(id = survey_id).exists():
            survey = Survey.objects.get(id = survey_id)
            # 序列化问卷的各项属性，并序列化其问题列表
            resp = {
                'content': content,
                'title': survey.title,
                'survey': survey.id,
                'description': survey.description,
                'public': survey.public,
                'modifiable': survey.modifiable,
                'activate': survey.activate,
                'questions': list(
                    Question.objects.filter(
                        survey = survey
                    ).values(
                        'id', 'order', 'topic_type', 'topic', 
                        'answer_type', 'answers', 'blank'
                    ).order_by('order')
                )
            }
        else:
            resp = {
                'content': content,
            }
        return render(request, 'edit.html', resp)
    # 处理编辑器提交数据
    elif request.method == 'POST':
        survey_id = request.POST.get('survey', '')

        # 若未传入问卷ID，则表明该问卷为新生成
        if not survey_id:
            survey_id = Base62.BaseID()
        
        # 处理问卷编辑器数据
        if request.POST.get('type') == 'survey':
            user_name = request.user
            user = SurveyUser.objects.get(user__username = user_name)

            # 取其中有效数据更新至问卷
            post_data = {
                k: request.POST.get(k) if k in ('title', 'description') else request.POST.get(k) == 'on'
                for k in ('activate', 'public', 'modifiable', 'title', 'description')
            }

            if not request.POST.get('survey', ''):
                post_data['founder'] = user

            # 创建或更新问卷
            Survey.objects.update_or_create(
                id = survey_id,
                defaults = post_data,
            )
        # 处理问题编辑器数据
        elif request.POST.get('type') == 'question':
            survey = Survey.objects.get(id = survey_id)
            question_id = request.POST.get('question_id', '')
            if not question_id:
                question_id = Base62.BaseID()

            # 获取该问题所提交的信息
            topic = request.POST.get('topic', '')
            topic_type = request.POST.get('topic_type', '')
            answer_type = request.POST.get('answer_type', '')
            if topic_type and answer_type:
                # 处理选择题及多选题的答案列表
                if answer_type in ('select', 'checkbox'):
                    answers = request.POST.getlist('answers', [])
                    answers = list(filter(None, answers))
                else:
                    answers = []
                
                # 更新或创建问题
                q, created = Question.objects.update_or_create(
                    survey = survey,
                    id = question_id,
                    defaults = {
                        'topic_type': topic_type,
                        'topic': topic,
                        'answer_type': answer_type,
                        'answers': answers,
                    }
                )
                if created:
                    next_order = max(
                        list(
                            Question.objects.filter(
                                survey = survey
                            ).values_list(
                                'order', flat = True
                            )
                        ) + [0]
                    ) + 1
                    q.order = next_order
                    q.save()
            return redirect('/edit?survey=%s&content=question'%survey_id)
        # 处理问题删除请求
        elif request.POST.get('type') == 'delete_question':
            # 获取将被删除的问题
            question_id = request.POST.get('question_id', '')
            question_queryset = Question.objects.filter(id = question_id)
            if question_queryset.count() == 1:
                # 取问题的序号
                question = question_queryset.first()
                order = question.order
                # 将问题删除
                question.delete()
                # 将比该问题序号更大的问题的序号减一
                Question.objects.filter(
                    order__gt = order
                ).update(
                    order = F('order') - 1
                )
            return redirect('/edit?survey=%s&content=question'%survey_id)

        return redirect('/edit?survey=%s&content=survey'%survey_id)

    return page_not_found(request)

@login_required
def statistics(request):
    if request.method == 'GET':
        # 获取当前登录用户
        user_name = request.user
        user = SurveyUser.objects.get(user__username = user_name)
        # 分别获取所属于该用户的问卷、题目及解答
        survey_queryset = Survey.objects.filter(founder = user)
        # 管理员拥有所有文件权限
        if user.user.is_superuser:
            survey_queryset = Survey.objects.all()
        question_queryset = Question.objects.filter(survey__in = survey_queryset)
        solution_queryset = Solution.objects.filter(question__in = question_queryset)
        # 序列化近一周的用户提交记录
        # 获取日期列表
        start_date = datetime.date.today() - datetime.timedelta(days = 6)
        date_list = [start_date + datetime.timedelta(days = i) for i in range(7)]
        # 汇总出近一周的用户及匿名提交数量
        recently_solution = solution_queryset.filter(
            submission_time__gte=start_date, 
        ).values_list('submission_time__date')
        user_submit = dict(recently_solution.annotate(
            Count('surveyuser', distinct=True)
        ))
        anonymous_submit = dict(recently_solution.annotate(
            Count('anonymous', distinct=True)
        ))

        to_index_list = lambda x: [[i, v] for i, v in enumerate(x)]
        # 序列化渲染所需数据
        resp = {
            # 问卷数量、问题数量、参与用户数量、参与匿名用户数量
            'survey_count': survey_queryset.count(),
            'question_count': question_queryset.count(),
            **solution_queryset.aggregate(
                user_count = Count('surveyuser', distinct=True)
            ),
            **solution_queryset.aggregate(
                anonymous_count = Count('anonymous', distinct=True)
            ),
            # 日期列表
            'date_list': to_index_list(map(str, date_list)),
            # 用户提交数量列表
            'user_list': to_index_list([
                user_submit.get(d, 0)
                for d in date_list
            ]),
            # 匿名提交数量列表
            'anonymous': to_index_list([
                anonymous_submit.get(d, 0)
                for d in date_list
            ]),
            # 问卷清单， 同时汇总该问卷的出问题数量、提交用户数量、匿名用户数量
            'survey_list': survey_queryset.values(
                'id', 'title', 'description', 'creation_time',
            ).annotate(
                questions_count = Count(
                    'questions', 
                    distinct=True,
                ),
                surveyuser_count = Count(
                    'questions__solutions__surveyuser', 
                    distinct=True,
                ),
                anonymous_count = Count(
                    'questions__solutions__anonymous', 
                    distinct=True,
                    filter=~Q(questions__solutions__anonymous = ''),
                ),
            )
        }
        
        return render(request, 'statistics.html', resp)
    return page_not_found(request)


@login_required
def analysis(request):
    if request.method == 'GET':
        # 获取本次分析的问卷ID
        survey_id = request.GET.get('survey', '')
        survey = Survey.objects.get(id = survey_id)
        queryset = Question.objects.filter(survey = survey)
        # 构造渲染数据列表，包含问题的各项属性
        resp = {
            'questions': queryset.values(
                'id', 'order', 'topic_type', 'topic', 'answer_type', 'answers'
            ).order_by('order')
        }
        for q in resp['questions']:
            # 汇总统计各个问题的答题情况
            answers = Solution.objects.filter(
                question = q['id']
            ).values_list('answer', flat=True)
            # 多选题需额外处理
            if q['answer_type'] == 'checkbox':
                answers = [a for ans in answers for a in eval(ans)]
            c = Counter(answers)
            length = len(answers)
            # 从频率的高到低对答题情况进行排序，并计算百分比
            solutions = [
                [k, (v / length) * 100]
                for k, v in c.most_common()
            ]
            q['solutions'] = solutions[:10]

        return render(request, 'analysis.html', resp)

    return page_not_found(request)

def page_not_found(request, exception = None):
    return render(request, '404.html')

def internal_server_error(request, exception = None):
    return render(request, '500.html', {'error': str(exception)})