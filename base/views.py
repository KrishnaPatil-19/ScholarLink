import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, Hub
from .forms import RoomForm, UserForm, MyUserCreationForm

EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

TOPIC_SYNONYMS = {
    'python': {'django', 'flask', 'numpy', 'pandas', 'python3', 'programming', 'code'},
    'data': {'analytics', 'statistics', 'dataset', 'datasets', 'ml', 'ai', 'machine', 'learning'},
    'machine': {'learning', 'ai', 'ml', 'neural', 'model', 'models'},
    'learning': {'machine', 'ai', 'ml', 'training', 'models'},
    'web': {'frontend', 'backend', 'html', 'css', 'javascript', 'js', 'react', 'node'},
    'django': {'python', 'web', 'backend', 'rest'},
    'java': {'spring', 'hibernate', 'jvm', 'kotlin'},
    'js': {'javascript', 'react', 'node', 'vue', 'angular'},
    'math': {'algebra', 'calculus', 'geometry', 'statistics'},
    'science': {'physics', 'chemistry', 'biology', 'research'},
}


def _normalize_words(text):
    return set(re.findall(r"\w+", text.lower()))


def is_message_on_topic(body, topic_name):
    if not body:
        return False
    if not topic_name:
        return True

    body_words = _normalize_words(body)
    topic_words = _normalize_words(topic_name)

    if body_words & topic_words:
        return True

    for token in topic_words:
        if token in TOPIC_SYNONYMS and body_words & TOPIC_SYNONYMS[token]:
            return True

    return False

# rooms = [
#     {'id': 1, 'name': 'Room 1'},
#     {'id': 2, 'name': 'Room 2'},
#     {'id': 3, 'name': 'Room 3'},
# ]

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'

        if not email or not password:
            messages.error(request, 'Email and password are required.')
        elif not re.match(EMAIL_REGEX, email):
            messages.error(request, 'Invalid email address format.')
        else:
            email = email.lower()
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # browser close
                messages.success(request, 'Logged in successfully.')
                return redirect('home')
            else:
                # Generic message to protect security
                messages.error(request, 'Invalid email or password.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()

            # Re-authenticate so Django knows which backend authenticated the user.
            authenticated_user = authenticate(
                request,
                email=user.email,
                password=form.cleaned_data['password1'],
            )
            if authenticated_user is not None:
                login(request, authenticated_user)

            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            # Show all form errors for easier debugging and user feedback
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"{error}")
                    else:
                        messages.error(request, f"{field}: {error}")

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    active_spaces = Hub.objects.all()[0:6]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q), is_removed=False)[0:3]

    context = {
        'rooms': rooms,
        'topics': topics,
        'active_spaces': active_spaces,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.filter(parent__isnull=True, is_removed=False)
    participants = room.participants.all()
    flagged_message = request.session.pop('flagged_message', '')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        body = request.POST.get('body', '').strip()
        reply_to = request.POST.get('reply_to')

        if body:
            parent = Message.objects.get(id=reply_to) if reply_to else None
            is_flagged = not is_message_on_topic(body, room.topic.name if room.topic else '')
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body,
                parent=parent,
                is_flagged=is_flagged,
                is_removed=is_flagged,
                flag_reason='Off-topic: does not match room topic' if is_flagged else ''
            )

            if is_flagged:
                request.session['flagged_message'] = body[:250]
                messages.warning(request, 'Your message was flagged and removed because it is off-topic for this room topic.')
            else:
                room.participants.add(request.user)

            return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
        'flagged_message': flagged_message,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def voteMessage(request, pk, action):
    message = Message.objects.get(id=pk)

    if request.user == message.user:
        messages.error(request, 'Cannot vote on your own message.')
        return redirect('room', pk=message.room.id)

    if action == 'upvote':
        message.downvoted_by.remove(request.user)
        message.upvoted_by.add(request.user)
    elif action == 'downvote':
        message.upvoted_by.remove(request.user)
        message.downvoted_by.add(request.user)

    return redirect('room', pk=message.room.id)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    spaces = Hub.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        hub_name = request.POST.get('space')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        hub = None
        if hub_name:
            hub, created = Hub.objects.get_or_create(name=hub_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            hub=hub,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'topics': topics, 'spaces': spaces}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    spaces = Hub.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        hub_name = request.POST.get('space')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        hub = None
        if hub_name:
            hub, created = Hub.objects.get_or_create(name=hub_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.hub = hub
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'spaces': spaces, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            if not is_message_on_topic(body, message.room.topic.name if message.room.topic else ''):
                messages.error(request, 'Message update blocked because it is off-topic for this room topic.')
            else:
                message.body = body
                message.is_flagged = False
                message.is_removed = False
                message.flag_reason = ''
                message.save()
                messages.success(request, 'Message updated successfully.')
                return redirect('room', pk=message.room.id)

        else:
            messages.error(request, 'Message cannot be empty.')

    return render(request, 'base/message_form.html', {'message': message})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room_id = message.room.id
        message.delete()
        return redirect('room', pk=room_id)
    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        email = request.POST.get('email', '').lower()

        if email and not re.match(EMAIL_REGEX, email):
            messages.error(request, 'Invalid email address format.')
        elif form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.filter(is_removed=False)
    return render(request, 'base/activity.html', {'room_messages': room_messages})

def debug_allauth(request):
    try:
        output = Template(
            "{% load socialaccount %}{% provider_login_url 'google' %}"
        ).render(Context())

        return HttpResponse(f"""
        <h2>SUCCESS</h2>
        <p>provider_login_url rendered successfully.</p>
        <p><strong>Output:</strong> {output}</p>
        """)

    except Exception:
        import traceback

        return HttpResponse(
            f"<pre>{traceback.format_exc()}</pre>",
            content_type="text/html",
        )