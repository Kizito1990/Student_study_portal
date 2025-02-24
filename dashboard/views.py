from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
from youtubesearchpython import VideosSearch




# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')
  

def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user = request.user, title = request.POST['title'], description = request.POST['description'])
            notes.save()
            messages.success(request, f"Note added from {request.user.username} successfully")
            return redirect('notes')
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user =request.user)
    context = {
        'notes':notes,
        'form':form
    }
    return render(request, 'dashboard/notes.html', context)

def delete_note(request, pk=None):
    Notes.objects.get(id = pk).delete()
    return redirect("notes")

class NoteDetailView(generic.DetailView):
    model = Notes
   

def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished =True
                else:
                    finished = False

            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished,

            )
            homeworks.save()
            messages.success(request, f'{request.user.username}, your homework was added successfully')
            return redirect('homework')
    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user = request.user)
    

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    context = {
        'homeworks':homeworks,
        'homework_done':homework_done,
        'form':form,
    }
    return render(request, 'dashboard/homework.html', context)



def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')


def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')


def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use .get() to avoid KeyError
        video = VideosSearch(text, limit=10) 
        
        result_list = []
        video_results = video.result().get('result', [])  # Ensure no KeyError
        
        for i in video_results:
            result_dict = { 
                'input': text,
                'title': i.get('title', 'No Title'),
                'duration': i.get('duration', 'N/A'),
                'thumbnail': i.get('thumbnails', [{}])[0].get('url', ''),  # Get first thumbnail safely
                'channel': i.get('channel', {}).get('name', 'Unknown Channel'),
                'link': i.get('link', '#'),
                'views': i.get('viewCount', {}).get('short', 'No Views'),
                'published': i.get('publishedTime', 'Unknown Date')
            }

            # Handle missing 'descriptionSnippet'
            desc = ''
            if 'descriptionSnippet' in i and i['descriptionSnippet']:
                desc = ''.join([j.get('text', '') for j in i['descriptionSnippet']])
            
            result_dict['description'] = desc
            result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,  # Pass results to template
        }
        return render(request, 'dashboard/youtube.html', context)
    
    else:
        form = DashboardForm()

    return render(request, 'dashboard/youtube.html', {'form': form})


def todo(request):
    todo = Todo.objects.filter(user = request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST)
                
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished =True
                else:
                    finished = False

            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request, f'You have added a Todo Item,{request.user.username}')
            return redirect('todo')
    else:
        form = TodoForm()
        if len(todo) == 0:
            todo_done = True
        else:
            todo_done = False 

    context = {
        'todos':todo,
        'form':form,
        'todo_done':todo_done,

    }
    return render(request, 'dashboard/todo.html', context)



def update_todo(request, pk=None):
    todos = Todo.objects.get(id=pk)
    if todos.is_finished == True:
        todos.is_finished = False
    else:
        todos.is_finished = True
    todos.save()
    return redirect('todo')

def delete_todo(request, pk):
    Todo.objects.get(id = pk).delete()
    return redirect('todo')




def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use .get() to prevent KeyError
        url = f"https://www.googleapis.com/books/v1/volumes?q={text}"
        
        try:
            r = requests.get(url, timeout=10)  # Set timeout for network stability
            r.raise_for_status()  # Raise an error for HTTP errors (e.g., 404, 500)
            answer = r.json()
        except requests.exceptions.RequestException as e:
            return render(request, 'dashboard/books.html', {'form': form, 'error': f"Error fetching books: {e}"})

        result_list = []
        if 'items' in answer:  # Check if the response contains 'items'
            for item in answer['items'][:10]:  # Safely iterate over available items
                volume_info = item.get('volumeInfo', {})

                result_dict = { 
                    'title': volume_info.get('title', 'No Title'),
                    'subtitle': volume_info.get('subtitle', 'No Subtitle'),
                    'description': volume_info.get('description', 'No Description'),
                    'count': volume_info.get('pageCount', 'N/A'),
                    'categories': volume_info.get('categories', []),
                    'rating': volume_info.get('averageRating', 'No Rating'),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', ''),  # Get the thumbnail
                    'preview': volume_info.get('previewLink', '#')  # Default to '#' if no preview link
                }

                result_list.append(result_dict)

        context = {
            'form': form,
            'results': result_list,  # Pass results to template
        }
        return render(request, 'dashboard/books.html', context)
    
    else:
        form = DashboardForm()

    return render(request, 'dashboard/books.html', {'form': form})
