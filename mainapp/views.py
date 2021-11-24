import datetime
from datetime import date

from django.core.files.base import ContentFile
from django.db.models import Sum, Count, Q
from django.db.models.functions import  ExtractMonth
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string, get_template
from django.contrib import messages
from io import BytesIO

from django.views import View
from xhtml2pdf import pisa

from .models import Projects, Employees, Comments, Tasks, Customers, STATUS_CHOICES, Archive, Company
from .forms import ProjectForm, CommentForm, CustomerForm
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required


@login_required
def test_view(request):
    totalp = Projects.objects.filter(status='Проектирование').count()
    totald = Projects.objects.filter(status='Дизайн').count()
    totalr = Projects.objects.filter(status='Разработка').count()
    totalv = Projects.objects.filter(status='Верстка').count()
    totals = Projects.objects.filter(status='Согласование').count()
    all_projects = Projects.objects.all()
    d = {'Проектирование': totalp, 'Дизайн': totald, 'Разработка': totalr, 'Верстка': totalv, 'Согласование': totals}
    return render(request, 'base.html', {'d': d, 'all_projects': all_projects})


@login_required
def index(request):
    return render(request, 'base.html')


@login_required
def project_list(request):
    return render(request, 'project_list.html', {})


@login_required
def project_list_all(request):
    data = dict()
    totalp = Projects.objects.filter(status='Проектирование').count()
    totald = Projects.objects.filter(status='Дизайн').count()
    totalr = Projects.objects.filter(status='Разработка').count()
    totalv = Projects.objects.filter(status='Верстка').count()
    totals = Projects.objects.filter(status='Согласование').count()
    all_projects = Projects.objects.all()
    today = date.today() + datetime.timedelta(days=8)
    d = {'Проектирование': totalp, 'Дизайн': totald, 'Разработка': totalr, 'Верстка': totalv, 'Согласование': totals}
    data['html_project_list'] = render_to_string('partial_project_list.html', {
        'today': today,
        'd': d,
        'all_projects': all_projects
    })
    return JsonResponse(data)


@login_required
def project_create(request):
    if 'p_id' in request.GET:
        p_id = request.GET['p_id']
        instance = get_object_or_404(Projects, id=p_id)
    else:
        instance = None
    if instance is None and request.user.groups.all()[0].name == 'Сотрудник':
        return redirect('project_list')
    form = ProjectForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('project_list')
    else:
        messages.error(request, "Error")
    return render(request, 'partial_project_create.html', {'instance': instance, 'form': form})


@login_required
def project_details(request, pk):
    data = {'id': '',
            'name': '',
            'status': '',
            'deadline': '',
            'curator': '',
            'customer': '',
            'description': '',
            'budget': '',
            'comments': ''}
    di = dict()
    project = Projects.objects.filter(id=pk)
    p = Projects.objects.get(id=pk)
    u = request.user.id - 1
    tasks = Tasks.objects.filter(project_id=pk)
    comms = Comments.objects.filter(project_id=pk)
    com_ar = []
    task_ar = []
    for i in comms:
        com_ar.append({
            'emp_id': i.emp_id,
            'comment': i.comment,
            'date': i.date
        })
    for j in tasks:
        task_ar.append({
            'name': j.name
        })
    data['id'] = project[0].id
    data['name'] = project[0].name
    data['status'] = project[0].status
    data['deadline'] = project[0].deadline
    data['description'] = project[0].description
    data['curator'] = project[0].curator
    data['customer'] = project[0].customer_id
    data['budget'] = project[0].budget
    data['tasks'] = task_ar
    data['comments'] = com_ar
    form = CommentForm(request.POST or None, initial={'project_id': p, 'emp_id': u})
    data['form'] = form
    if request.method == "POST":
        if form.is_valid:
            form.save()
            return redirect('project_list')
        else:
            messages.error(request, "Error")
    di['html_form'] = render_to_string('partial_project_details.html', data, request=request)
    return JsonResponse(di)


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Projects, id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'project_delete.html', {'project': project})


@login_required
def send_to_archive(request):
    if 'pk' in request.GET:
        pk = request.GET['pk']
    project = get_object_or_404(Projects, id=pk)
    company = Company.objects.get(id=1)
    tasks = Tasks.objects.filter(project_id=pk)
    task_ar = []
    for j in tasks:
        task_ar.append({
            'name': j.name
        })
    if request.method == 'POST':
        p = Archive(name=project.name,
                    customer_id=project.customer_id,
                    date=project.date,
                    deadline=project.deadline,
                    budget=project.budget,
                    contract=project.contract)
        p.save()
        data = {
            "company": company.name,
            "dir": company.director,
            "customer": project.customer_id,
            "customer_dir": Customers.objects.get(id=project.customer_id.id).director,
            "name": project.name,
            "date": project.date,
            "deadline": project.deadline,
            "budget": project.budget,
            "description": project.description,
            "tasks": task_ar,
        }
        pdf = render_act('act_template.html', data, p)
        project.delete()
        #return HttpResponse(pdf, content_type='application/pdf')
        return redirect('project_list')
    return render(request, 'project_done.html', {'project': project})


@login_required
def create_tasks(request):
    if 'pk' in request.GET:
        pk = request.GET['pk']
    TaskFormset = inlineformset_factory(Projects, Tasks, fields=('name',), extra=8, max_num=8, can_delete=True)
    project = Projects.objects.get(id=pk)
    tasks = Tasks.objects.filter(project_id=pk)
    form = TaskFormset(queryset=tasks, instance=project)
    if request.method == 'POST':
        form = TaskFormset(request.POST, queryset=tasks, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    return render(request, 'add_task.html', {'form': form})


def login_view(request):
    login(request)


def logout_view(request):
    logout(request)


@login_required
def emp_view(request):
    di = dict()
    all_employees = Employees.objects.all()
    for dept in STATUS_CHOICES:
        di[dept[0]] = []
    for emp in all_employees:
        data = {}
        dep = emp.post.department
        pr_cnt = Projects.objects.filter(curator=emp).count()
        data[emp] = pr_cnt
        di[dep].append(data)
    return render(request, 'employees.html', {'di': di})


@login_required
def cust_view(request):
    di = []
    all_customers = Customers.objects.all()
    for cust in all_customers:
        data = {}
        if len(Projects.objects.all().filter(customer_id=cust)) > 0:
            data[cust] = 'Активен'
            di.append(data)
        else:
            data[cust] = ''
            di.append(data)
    return render(request, 'customers.html', {'di': di})


@login_required
def contract_view(request):
    if request.user.groups.all()[0].name == 'Сотрудник':
        return redirect('project_list')
    di = []
    all_contracts = Projects.objects.all().exclude(contract='')
    all_archives = Archive.objects.all().order_by('-date')
    potentials = Projects.objects.all().filter(contract='')
    if request.method == 'POST':
        answer = request.POST.get('potential_contract')
        return redirect('pdf_view/?p_id=%s' % answer)
    for ctr in all_contracts:
        data = {}
        data[ctr] = 'В работе'
        di.append(data)
    for arch in all_archives:
        data = {}
        data[arch] = 'Готово'
        di.append(data)
    return render(request, 'contracts.html', {'di': di, 'potentials': potentials})


@login_required
def customer_details(request, pk):
    data = {'id': '',
            'name': '',
            'director': '',
            'phone': '',
            'email': '',
            'inn': '',
            'kpp': '',
            'bill_acc': '',
            'bik': ''}
    di = dict()
    customers = Customers.objects.filter(id=pk)
    data['id'] = customers[0].id
    data['name'] = customers[0].name
    data['director'] = customers[0].director
    data['phone'] = customers[0].phone
    data['email'] = customers[0].email
    data['inn'] = customers[0].inn
    data['kpp'] = customers[0].kpp
    data['bill_acc'] = customers[0].bill_acc
    data['bik'] = customers[0].bik
    di['html_form'] = render_to_string('partial_customer_details.html', data, request=request)
    return JsonResponse(di)


@login_required
def emp_details(request, pk):
    data = {'last_name': '',
            'first_name': '',
            'up_name': '',
            'post': '',
            'dept': '',
            'phone': '',
            'email': '',
            'image': ''}
    di = dict()
    emps = Employees.objects.filter(id=pk)
    data['last_name'] = emps[0].last_name
    data['first_name'] = emps[0].first_name
    data['up_name'] = emps[0].up_name
    data['post'] = emps[0].post
    data['dept'] = emps[0].post.department
    data['phone'] = emps[0].phone
    data['email'] = emps[0].email
    data['image'] = emps[0].image
    di['html_form'] = render_to_string('partial_emp_details.html', data, request=request)
    return JsonResponse(di)


@login_required
def add_customer(request):
    if 'cust_id' in request.GET:
        cust_id = request.GET['cust_id']
        instance = get_object_or_404(Customers, id=cust_id)
    else:
        instance = None
    form = CustomerForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('customers')
    return render(request, 'partial_customer_create.html', {'form': form})


@login_required
def my_projects(request):
    today = date.today() + datetime.timedelta(days=8)
    u = request.user.id - 1
    projects = Projects.objects.all().filter(curator_id=u)
    return render(request, 'my_projects.html', {'today': today, 'projects': projects})


@login_required
def validate_status(request):
    status = request.GET.get('status', None)
    li = Employees.objects.filter(post__department=status).values('id', 'first_name', 'last_name')
    return JsonResponse({'data': list(li)})


def render_act(template_src, context_dict, p):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    updated_file = ContentFile(result.getvalue())
    updated_file.name = "act.pdf"
    p.act = updated_file
    p.save()
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def render_to_pdf(template_src, context_dict, project):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    updated_file = ContentFile(result.getvalue())
    updated_file.name = "filename.pdf"

    project.contract = updated_file
    project.save()
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class ViewPDF(View):

    def get(self, request, *args, **kwargs):
        if 'p_id' in request.GET:
            p_id = request.GET['p_id']
        project = get_object_or_404(Projects, id=p_id)
        company = Company.objects.get(id=1)
        customer = Customers.objects.get(id=project.customer_id.id)
        tasks = Tasks.objects.filter(project_id=p_id)
        task_ar = []
        for j in tasks:
            task_ar.append({
                'name': j.name
            })
        data = {
            "company": company.name,
            "dir": company.director,
            "inn": company.inn,
            "kpp": company.kpp,
            "bill_acc": company.bill_acc,
            "bik": company.bik,
            "customer": customer.name,
            "customer_dir": customer.director,
            "customer_inn": customer.inn,
            "customer_kpp": customer.kpp,
            "customer_bill_acc": customer.bill_acc,
            "customer_bik": customer.bik,
            "name": project.name,
            "date": project.date,
            "deadline": project.deadline,
            "budget": project.budget,
            "description": project.description,
            "tasks": task_ar,
        }
        pdf = render_to_pdf('pdf_template.html', data, project)
        return HttpResponse(pdf, content_type='application/pdf')


def error_view(request):
    return render(request, 'oops.html', {})


def search(request):
    data = {}
    q = request.GET.get('q', None)
    today = date.today() + datetime.timedelta(days=8)
    totalp = Projects.objects.filter(status='Проектирование').count()
    totald = Projects.objects.filter(status='Дизайн').count()
    totalr = Projects.objects.filter(status='Разработка').count()
    totalv = Projects.objects.filter(status='Верстка').count()
    totals = Projects.objects.filter(status='Согласование').count()
    d = {'Проектирование': totalp, 'Дизайн': totald, 'Разработка': totalr, 'Верстка': totalv, 'Согласование': totals}
    if q:
        all_projects = Projects.objects.filter(name__icontains=q)
        data['html_project_list'] = render_to_string('partial_project_list.html', {
            'today': today,
            'd': d,
            'all_projects': all_projects
        })
    elif q == '':
        all_projects = Projects.objects.filter(name__icontains=q)
        data['html_project_list'] = render_to_string('partial_project_list.html', {
            'today': today,
            'd': d,
            'all_projects': all_projects
        })
    return JsonResponse(data)


def stats_view(request):
    return render(request, 'stats.html', {})


def stats_data(request):
    sd = request.GET.get('sd', None)
    ed = request.GET.get('ed', None)
    data = {'date_list': [],
            'amount_list': [],
            'count_list': [],
            'types': ['Сайты', 'Приложения', 'Айдентика', 'Другое'],
            'counts': []}
    if sd or ed:
        if not sd:
            sd = "2021-11-01"
        elif not ed:
            ed = date.today()
    else:
        sd = "2021-11-01"
        ed = date.today()
    all_projects = Archive.objects.all().filter(date__range=[sd, ed]) \
        .annotate(month=ExtractMonth('date')) \
        .values('month') \
        .annotate(amount=Sum('budget'), count=Count('id')) \
        .order_by('month')
    all_all = Archive.objects.all().filter(date__range=[sd, ed])
    for el in all_projects:
        if not el['month'] in data['date_list']:
            data['date_list'].append(el['month'])
            data['amount_list'].append(el['amount'])
            data['count_list'].append(el['count'])
    data['counts'].append(all_all.filter(Q(name__icontains='ендинг')
                                        | Q(name__icontains='айт')).count())
    data['counts'].append(all_all.filter(Q(name__icontains='риложени')
                                        | Q(name__icontains='app')).count())
    data['counts'].append(all_all.filter(Q(name__icontains='бук')
                                         | Q(name__icontains='тиль')).count())
    data['counts'].append(all_all.count()-sum(data['counts']))
    return JsonResponse(data)
