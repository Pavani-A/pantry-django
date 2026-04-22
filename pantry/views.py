from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
import requests
import re

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
    from datetime import timedelta
from django.utils import timezone

@login_required
def item_list(request):
    items = Item.objects.filter(user=request.user)

    today = timezone.now()
    soon = today + timedelta(days=2)

    expiring_items = []

    for item in items:
        if item.exp_date:
            if item.exp_date < today:
                item.status = "expired"
            elif item.exp_date <= soon:
                item.status = "expiring"
                expiring_items.append(item)   # 🔥 store for popup
            else:
                item.status = "fresh"
        else:
            item.status = "no_date"

    return render(request, 'pantry/item_list.html', {
        'products': items,
        'expiring_items': expiring_items   # 🔥 send to UI
    })


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

@login_required
def suggest_recipes(request):
    # 🔍 Get search input
    ingredient = request.GET.get('ingredient')

    items = Item.objects.filter(user=request.user)

    # 👉 If user didn't search → use pantry
    if not ingredient:
        if items:
            ingredient = items[0].name.lower()
        else:
            ingredient = "chicken"  # fallback

    # 🔥 API call
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    response = requests.get(url)
    data = response.json()

    recipes = data.get('meals', [])

    return render(request, 'pantry/recipes.html', {
        'recipes': recipes,
        'ingredient': ingredient
    })

@login_required
def recipe_detail(request, meal_id):

    # 🔹 Get selected recipe
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    response = requests.get(url)
    data = response.json()

    recipe = data['meals'][0]   # ❗ YOU MISSED THIS

    # 🔹 Clean instructions
    raw_text = recipe.get('strInstructions', '')
    clean_text = raw_text.replace('▢', '')

    instructions = re.split(r'\.\s+', clean_text)
    instructions = [step.strip() for step in instructions if step.strip()]

    # 🔹 Get related recipes (same category)
    category = recipe.get('strCategory')

    related_url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}"
    related_response = requests.get(related_url)
    related_data = related_response.json()

    related_recipes = related_data.get('meals', [])

    # ❗ remove current recipe from list
    related_recipes = [
        item for item in related_recipes if item['idMeal'] != meal_id
    ][:5]   # limit to 5

    return render(request, 'pantry/recipe_detail.html', {
        'recipe': recipe,
        'instructions': instructions,
        'related_recipes': related_recipes   # 🔥 needed for sidebar
    })