from django.shortcuts import render,redirect
from .models import Task
from.forms import TaskForm

# Create your views here.

def home(request):
    tasks = Task.objects.all()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    else:
        form = TaskForm()

    context = {
        'tasks':tasks,
        'TaskForm':form
    }
    return render(request, 'Todo/home.html', context)


def task_update(request, pk):
    task = Task.objects.get(id = pk)
    form = TaskForm(instance=task)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'form':form
    }


    return render(request, 'Todo/task_update.html', context)


def delete(request, pk):
    task = Task.objects.get(id = pk)
    if request.method == 'POST':
        task.delete()
        return redirect('/')
    return render(request, 'Todo/delete.html')


