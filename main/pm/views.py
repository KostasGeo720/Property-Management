from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Property, Lease, Problem
from .forms import NewPropertyForm, NewLeaseForm, NewProblemForm

# Create your views here.
@login_required
def home(request):
    problems = Problem.objects.filter(property__owner=request.user).order_by('-created_at')
    return render(request, 'pm/home.html', {'problems':problems})

@login_required
def create_property(request):
    if request.method == 'POST':
        form = NewPropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            messages.success(request, 'Property created successfully!')
            return redirect('home')
    else:
        form = NewPropertyForm()
    return render(request, 'pm/create_property.html', {'form': form})

@login_required
def create_lease(request):
    if request.method == 'POST':
        form = NewLeaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lease created successfully!')
            return redirect('home')
    else:
        form = NewLeaseForm()
    return render(request, 'pm/create_lease.html', {'form': form})

@login_required
def report_problem(request):
    if request.method == 'POST':
        form = NewProblemForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.tenant = request.user
            problem.save()
            messages.success(request, 'Problem reported successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewProblemForm()
    return render(request, 'pm/report_problem.html', {'form': form})

@login_required
def solve_problem(request, problem_id):
    problem = Problem.objects.get(id=problem_id)
    problem.delete()
    messages.success(request, 'Problem sarked as solved successfully!')
    return redirect('home')

@login_required
def manage_properties(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'pm/manage_properties.html', {'properties':properties})

@login_required
def status_price(request, property_id):
    property = Property.objects.get(id=property_id)
    if property.price_status in ('negotiable', 'Negotiable'):
        property.price_status = 'fixed'
        property.save()
        messages.success(request, 'Price status changed to fixed successfully!')
    else:
        property.price_status = 'negotiable'
        property.save()
        messages.success(request, 'Price status changed to negotiable successfully!')
    return redirect('manage_properties')

@login_required
def status_rent(request, property_id):
    property = Property.objects.get(id=property_id)
    if property.rent_price_status in ('negotiable', 'Negotiable'):
        property.rent_price_status = 'fixed'
        property.save()
        messages.success(request, 'Rent price status changed to fixed successfully!')
    else:
        property.rent_price_status = 'negotiable'
        property.save()
        messages.success(request, 'Rent price status changed to negotiable successfully!')
    return redirect('manage_properties')