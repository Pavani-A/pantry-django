from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# 🔐 SIGNUP
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)

        # 🔥 Auto login after signup
        login(request, user)
        messages.success(request, "Account created successfully ✅")

        return redirect('item_list')

    return render(request, 'pantry/signup.html')


# 🔐 LOGIN
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('item_list')
        else:
            messages.error(request, "Invalid credentials ❌")
            return redirect('login')

    return render(request, 'pantry/login.html')


# 🔐 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


# 🏠 HOME (NO LOGIN REQUIRED)
def home(request):
    return render(request, 'pantry/home.html')


# 📦 VIEW ITEMS (USER-SPECIFIC)
@login_required
def item_list(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'pantry/item_list.html', {'products': items})


# ➕ ADD ITEM
@login_required
def add_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        exp_date = request.POST.get('exp_date')

        Item.objects.create(
            user=request.user,   # 🔥 IMPORTANT
            name=name,
            quantity=quantity,
            exp_date=exp_date
        )

        messages.success(request, "Item added successfully ✅")
        return redirect('item_list')

    return render(request, 'pantry/add_item.html')


# 🗑️ DELETE ITEM (SECURE)
@login_required
def delete_item(request, id):
    item = get_object_or_404(Item, id=id, user=request.user)
    item.delete()

    messages.success(request, "Item deleted successfully 🗑️")
    return redirect('item_list')


# ✏️ EDIT ITEM (SECURE)
@login_required
def edit_item(request, id):
    item = get_object_or_404(Item, id=id, user=request.user)

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.quantity = request.POST.get('quantity')
        item.exp_date = request.POST.get('exp_date')
        item.save()

        messages.success(request, "Item updated successfully ✏️")
        return redirect('item_list')

    return render(request, 'pantry/edit_item.html', {'item': item})