
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from django.contrib import messages

def home(request):
    return render(request, 'pantry/home.html')

def item_list(request):
    items = Item.objects.all()
    return render(request, 'pantry/item_list.html', {'products': items})

def add_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        exp_date = request.POST.get('exp_date')
        Item.objects.create(name=name, quantity=quantity, exp_date=exp_date)
        messages.success(request, "Item added successfully ✅")
        return redirect('/view/')
    return render(request, 'pantry/add_item.html')

def delete_item(request, id):
    item = get_object_or_404(Item, id=id)
    item.delete()
    messages.success(request, "Item deleted successfully ✅")
    return redirect('/view/')

def edit_item(request, id):
    item = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.quantity = request.POST.get('quantity')
        item.exp_date = request.POST.get('exp_date')
        item.save()
        messages.success(request, "Item updated successfully ✅")
        return redirect('/view/')
    return render(request, 'pantry/edit_item.html', {'item': item}) 