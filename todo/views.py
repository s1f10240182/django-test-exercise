from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task
from django.db import models

from datetime import timedelta
from django.utils import timezone

# Create your views here.
def index(request):
    if request.method == 'POST':
        priority = request.POST.get('priority', 'medium')
        task = Task(title=request.POST['title'],
                    due_at=make_aware(parse_datetime(request.POST['due_at'])),
                    priority=priority)
        task.save()

    now = timezone.now()
    upcoming_tasks = Task.objects.filter(
        completed=False,
        due_at__isnull=False,
        due_at__gte=now,
        due_at__lte=now + timedelta(days=3)
    ).order_by('due_at')

    order = request.GET.get('order')
    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    elif order == 'priority':
        tasks = Task.objects.order_by(
            models.Case(
                models.When(priority='high', then=0),
                models.When(priority='medium', then=1),
                models.When(priority='low', then=2),
                default=3,
                output_field=models.IntegerField(),
            ),
            'due_at'
        )
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks
    }

    context['upcoming_tasks'] = upcoming_tasks
    
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not exist')
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.priority = request.POST.get('priority', 'medium')
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, 'todo/edit.html', context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)

def delete_closed(request):
    Task.objects.filter(completed=True).delete()
    return redirect(index)

def toggle_complete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    task.completed = not task.completed
    task.save()
    return redirect(index)
