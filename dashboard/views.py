from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests, wikipedia
from youtubesearchpython import VideosSearch
from django.contrib.auth.decorators import login_required





# Create your views here.
@login_required
def home(request):
    return render(request, 'dashboard/home.html')
  
@login_required
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
@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id = pk).delete()
    return redirect("notes")

class NoteDetailView(generic.DetailView):
    model = Notes
   
@login_required
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


@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
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

@login_required
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


@login_required
def update_todo(request, pk=None):
    todos = Todo.objects.get(id=pk)
    if todos.is_finished == True:
        todos.is_finished = False
    else:
        todos.is_finished = True
    todos.save()
    return redirect('todo')
@login_required
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


'''def dictionary(request):

    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use .get() to prevent KeyError
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US"+text
        r = requests.get(url)
   
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio': audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms,
            }
        except:
            context = {
            'form':form,
            'input':''
        }
        return render(request, "dashboard/dictionary.html", context) 
    else:
        form = DashboardForm()
        context = {
        'form':form
        }
    return render(request, "dashboard/dictionary.html", context) 
'''
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '').strip()  # Remove any extra spaces
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        
        try:
            r = requests.get(url, timeout=10)  # Set a timeout to avoid hanging requests
            r.raise_for_status()  # Raise an error for HTTP failures (e.g., 404, 500)
            answer = r.json()

            # Extract data safely using .get() and list indexing checks
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'No phonetics available')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
            definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'No definition found')
            example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', 'No example available')
            synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms,
            }
        except requests.exceptions.RequestException as e:  # Handle API request errors
            context = {
                'form': form,
                'input': text,
                'error': f"Error fetching definition: {e}",
            }
        except (KeyError, IndexError):  # Handle missing dictionary fields
            context = {
                'form': form,
                'input': text,
                'error': "Word not found. Please try another word.",
            }

        return render(request, "dashboard/dictionary.html", context)
    
    else:
        form = DashboardForm()
        return render(request, "dashboard/dictionary.html", {'form': form})

def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context ={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
    
        return render(request,'dashboard/wiki.html', context)
        
    else:
        form = DashboardForm()
        context = {
            'form':form
    }
    return render(request, 'dashboard/wiki.html', context)

def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form': measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''

                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} foot = {int(input)/3} yard'
                context = {
                'form':form,
                'm_form': measurement_form,
                'input':True,
                'answer':answer
            }
        
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form': measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''

                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                context = {
                'form':form,
                'm_form': measurement_form,
                'input':True,
                'answer':answer
            }
    else:
        form = ConversionForm()

        context = {
            'form':form,
            'input':False
    }
    return render(request, 'dashboard/conversion.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account has been created for {username}')
            return redirect('login')
           
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    }

    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user = request.user)
    todos = Todo.objects.filter(is_finished = False, user = request.user)

    if len(homeworks) > 0:
        homework_done = False
    else:
        homework_done = True
    

    if len(todos) > 0:
        todos_done = False
    else:
        todos_done = True

    context = {
        'homeworks':homeworks,
        'homework_done':homework_done,
        'todos_done':todos_done,
        'todos':todos,
    }
    return render(request, 'dashboard/profile.html', context)