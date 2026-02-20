from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemForm

@login_required
def quotation_list(request):
    quotations = request.user.quotations.all().order_by('-created_at')
    return render(request, 'quotations/quotation_list.html', {'quotations': quotations})

@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk, user=request.user)
    items = quotation.items.all()
    return render(request, 'quotations/quotation_detail.html', {
        'quotation': quotation,
        'items': items
    })

@login_required
def create_quotation(request):
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.user = request.user
            quotation.save()
            messages.success(request, 'Quotation created!')
            return redirect('quotations:quotation_detail', pk=quotation.pk)
    else:
        form = QuotationForm()
    return render(request, 'quotations/create_quotation.html', {'form': form})

@login_required
def add_quotation_item(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk, user=request.user)
    if request.method == 'POST':
        form = QuotationItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quotation = quotation
            item.save()
            messages.success(request, 'Item added to quotation!')
            return redirect('quotations:quotation_detail', pk=quotation.pk)
    else:
        form = QuotationItemForm()
    return render(request, 'quotations/add_item.html', {'form': form, 'quotation': quotation})

@login_required
def delete_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk, user=request.user)
    quotation.delete()
    messages.success(request, 'Quotation deleted!')
    return redirect('quotations:quotation_list')
