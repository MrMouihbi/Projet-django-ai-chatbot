from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
import openai
from .models import Chat
from django.utils import timezone

# Create your views here.

openai.api_key = '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'

def ask_openai(message):
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )

    answer = response.choices[0].text
    return answer

def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user=user)
            return redirect('chatbot')
        else:
            return render(request, "login.html", {'error_message': "Wrong email or password"})
    else:
        return render(request, "login.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                return render(request, "register.html", {'error_message': "An error occurred"})
        else:
            return render(request, "register.html", {'error_message': "Passwords don't match"})
    return render(request, "register.html")

def logout(request):
    auth.logout(request)
    return redirect('login')