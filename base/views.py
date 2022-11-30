from http.client import INTERNAL_SERVER_ERROR, REQUEST_HEADER_FIELDS_TOO_LARGE
from tkinter import HIDDEN
from xmlrpc.client import Boolean
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, Reserve
from .forms import RoomForm, UserForm, ReserveForm


# Create your views here.

#rooms =[
   # {'id':1, 'name': 'Lets learn python!'},
  #  {'id':2, 'name': 'design with me'},
 #   {'id':3, 'name': 'frontend'},
#]


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=="POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):  
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect ('home')
        else:
            messages.error(request, 'An error has occured')

    return render(request, 'base/login_register.html',{'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(author__icontains=q) |
        Q(serialnumber__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()[0:5]
    room_count =rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))


    context = {'rooms':rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request,'base/home.html',context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(    
            user=request.user,
            room=room,
            body= request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect ('room', pk=room.id)

    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'base/room.html',context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    room_messages = user.message_set.all()
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms' : rooms, 'room_messages' : room_messages,'topics' : topics}
    return render(request, 'base/profile.html', context)






@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.author = request.POST.get('author')
        room.serialnumber = request.POST.get('serialnumber')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


    context = {'form':form , 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)


        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            author=request.POST.get('author'),
            serialnumber=request.POST.get('serialnumber'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form':form , 'topics':topics}
    return render(request, 'base/room_form.html', context)

#########################
# @login_required(login_url='login')
# def createReserve(request):
#     form = ReserveForm()
#     borrower = Reserve.objects.all()

#     if request.method == 'POST':
#         borrower_name = request.POST.get('borrowername')
#         borrower, created = Topic.objects.get_or_create(name=borrower_name)

#         Room.objects.create(
#             borrowername=request.user,
#             name=request.POST.get('name'),
#             author=request.POST.get('author'),
#             serialnumber=request.POST.get('serialnumber'),
#         )
#         return redirect('home')
#     bname = Reserve.objects.get(borrower_name)

#     context = {'form':form , 'borrowername':borrower, 'bname':bname}
#     return render(request, 'base/request.html', context)
#############################
def requestbtn(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        Room.objects.filter(id=pk).update(status = 1)
        return redirect('home')
    return render (request,'base/request.html', {'obj':room})


@login_required(login_url='login')
def confirmresbtn(request, pk):
    room = Room.objects.get(id=pk)


    if request.method == 'POST':

        Room.objects.filter(id=pk).update(status = 2)

        return redirect('home')

    
    return render(request, 'base/confirmres.html', {'obj':room})

@login_required(login_url='login')
def returnBook(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        Room.objects.filter(id=pk).update(status = 0)
        return redirect('home')

    return render(request, 'base/returned.html', {'obj':room})


@login_required(login_url='login')
def denyBook(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        Room.objects.filter(id=pk).update(status = 0)
        return redirect('home')

    return render(request, 'base/denied.html', {'obj':room})




@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})




@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)


    return render (request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render (request, 'base/activity.html', {'room_messages':room_messages})