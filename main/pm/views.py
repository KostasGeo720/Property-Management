from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Property, Lease, Problem, Message, Document, PropertyComplex, Unit, Expense
from .forms import NewPropertyForm, NewLeaseForm, NewProblemForm, AddTenantForm, DocumentForm, NewPropertyComplexForm, NewUnitForm, ExpenseForm

# Create your views here.

def update_status(request):
    # Get leases for both properties and units owned by the user
    property_leases = Lease.objects.filter(property__owner=request.user)
    unit_leases = Lease.objects.filter(unit__owner=request.user)
    
    # Combine both querysets
    leases = property_leases.union(unit_leases)
    
    for lease in leases:
        lease.update_payment_status()

@login_required
def home(request):
    property_problems = Problem.objects.filter(property__owner=request.user).order_by('-created_at')
    unit_problems = Problem.objects.filter(unit__owner=request.user).order_by('-created_at')
    problems = property_problems | unit_problems
    notifications = Message.objects.filter(owner=request.user).order_by('-timestamp')
    properties = Property.objects.filter(lease__tenant=request.user).distinct()
    units = Unit.objects.filter(lease__tenant=request.user).distinct()
    update_status(request)
    return render(request, 'pm/home.html', {'problems':problems, 'notifications':notifications, 'properties': properties, 'units': units})

@login_required
def create_property_complex(request):
    if request.method == 'POST':
        form = NewPropertyComplexForm(request.POST)
        if form.is_valid():
            property_complex = form.save(commit=False)
            property_complex.owner = request.user
            property_complex.save()
            messages.success(request, 'Το συγκρότημα ακινήτων δημιουργήθηκε επιτυχώς!')
            return redirect('manage_properties')
    else:
        form = NewPropertyComplexForm()
    return render(request, 'pm/create_property_complex.html', {'form': form})

@login_required
def create_unit(request, address):
    complex_obj = PropertyComplex.objects.get(address=address)

    if request.method == 'POST':
        form = NewUnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.owner = request.user
            unit.complex = complex_obj
            unit.save()
            messages.success(request, 'Η μονάδα προστέθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα! Παρέχονται μη έγκυρα δεδομένα.')
    else:
        form = NewUnitForm()

    return render(request, 'pm/create_property.html', {'form': form, 'complex': complex_obj})

@login_required
def create_property(request):
    if request.method == 'POST':
        form = NewPropertyForm(request.POST)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            messages.success(request, 'Το ακίνητο προστέθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα! Παρέχονται μη έγκυρα δεδομένα.')
    else:
        form = NewPropertyForm()
    return render(request, 'pm/create_property.html', {'form': form})

@login_required
def new_property_page(request):
    if request.method == 'POST':
        if request.POST.get('property_type') == 'complex':
            return redirect('create_property_complex')
        else:
            return redirect('create_property')
    return render(request, 'pm/new_property_page.html')

@login_required
def create_lease(request, property_id):
    property = Property.objects.get(id=property_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, landlord_user=request.user)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.property = property
            lease.save()
            form.save_m2m()
            property.status = 'rented'
            property.save()
            messages.success(request, 'Η μίσθωση δημιουργήθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewLeaseForm(landlord_user=request.user)
    return render(request, 'pm/create_lease.html', {'form': form})

@login_required
def create_lease_unit(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, landlord_user=request.user)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.unit = unit
            lease.save()
            form.save_m2m()
            unit.status = 'rented'
            unit.save()
            messages.success(request, 'Η μίσθωση δημιουργήθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewLeaseForm(landlord_user=request.user)
    return render(request, 'pm/create_lease.html', {'form': form, 'unit': unit})

@login_required
def report_problem(request):
    properties = Property.objects.filter(lease__tenant=request.user).distinct()
    units = Unit.objects.filter(lease__tenant=request.user).distinct()
    if request.method == 'POST':
        form = NewProblemForm(request.POST, tenant=request.user)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.tenant = request.user
            problem.save()
            messages.success(request, 'Το πρόβλημα αναφέρθηκε επιτυχώς!')
            return redirect('home')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewProblemForm(tenant=request.user)
    return render(request, 'pm/report_problem.html', {'form': form, 'properties': properties, 'units': units})

@login_required
def solve_problem(request, problem_id):
    problem = Problem.objects.get(id=problem_id)
    problem.delete()
    messages.success(request, 'Το πρόβλημα σημειώθηκε ως επιλυμένο επιτυχώς!') #Femboy Spelling Correction
    return redirect('home')

@login_required
def manage_properties(request):
    update_status(request)
    leases = Lease.objects.filter(property__owner=request.user).order_by('-created_at')
    leased_properties = [lease.property.id for lease in leases]
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    complexes = PropertyComplex.objects.filter(owner=request.user).order_by('-created_at')
    units = Unit.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'pm/manage_properties.html', {'properties':properties, 'leases':leases, 'leased_properties':leased_properties, 'complexes':complexes, 'units':units})

@login_required
def remove_tennant(request, lease_id, tennant_id):
    lease = Lease.objects.get(id=lease_id)
    tennant = User.objects.get(id=tennant_id)
    lease.tennant.remove(tennant)
    messages.success(request, 'Ο ενοικιαστής αφαιρέθηκε επιτυχώς!')
    if lease.tennant.count() == 0:
        lease.property.status = 'available'
        lease.delete()
    lease.save()
    return redirect('leases')

@login_required
def add_tennant(request, property_id):
    property = Property.objects.get(id=property_id)
    lease = Lease.objects.get_or_create(property=property)[0]
    if request.method == 'POST':
        form = AddTenantForm(request.POST, instance=lease)
        if form.is_valid():
            selected_tenants = form.cleaned_data['tennant']
            tenant_ids = [tenant.id for tenant in selected_tenants]
            messages.success(request, 'Ο ενοικιαστής προστέθηκε επιτυχώς!')
            return redirect(f'/create_lease/{property_id}/?tenants={",".join(map(str, tenant_ids))}')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = AddTenantForm(instance=lease)
    return render(request, 'pm/add_tennant.html', {'form':form})

@login_required
def edit_property(request, property_id):
    property = Property.objects.get(id=property_id)
    if request.method == 'POST':
        form = NewPropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, 'Το ακίνητο ενημερώθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewPropertyForm(instance=property)
    return render(request, 'pm/edit_property.html', {'form': form})

@login_required
def manage_unit(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    lease = Lease.objects.filter(unit=unit).first()
    if request.method == 'POST':
        form = NewUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η μονάδα ενημερώθηκε επιτυχώς!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewUnitForm(instance=unit)
    return render(request, 'pm/manage_unit.html', {'form': form, 'unit': unit, 'lease': lease})

@login_required
def edit_lease(request, property_id):
    update_status(request)
    lease = Lease.objects.get(property__id=property_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, instance=lease, landlord_user=request.user)
        if form.is_valid():
            l = form.save(commit=False)
            if l.tenant.count() == 0:
                messages.error(request, 'Η μίσθωση πρέπει να έχει τουλάχιστον έναν ενοικιαστή!')
            else:
                form.save()
                messages.success(request, 'Η μίσθωση ενημερώθηκε επιτυχώς!')
                return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewLeaseForm(instance=lease, landlord_user=request.user)
    return render(request, 'pm/edit_lease.html', {'form': form, 'lease': lease})

@login_required
def edit_lease_unit(request, unit_id):
    update_status(request)
    lease = Lease.objects.get(unit__id=unit_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, instance=lease, landlord_user=request.user)
        if form.is_valid():
            l = form.save(commit=False)
            if l.tenant.count() == 0:
                messages.error(request, 'Lease must have at least one tenant!')
            else:
                form.save()
                messages.success(request, 'Η μίσθωση ενημερώθηκε επιτυχώς!')
                return redirect('manage_properties')
        else:
            messages.error(request, 'Σφάλμα!')
    else:
        form = NewLeaseForm(instance=lease, landlord_user=request.user)
    return render(request, 'pm/edit_lease.html', {'form': form, 'lease': lease})

@login_required
def delete_property(request, property_id):
    property = Property.objects.get(id=property_id)
    property.delete()
    messages.success(request, 'Το ακίνητο διαγράφηκε επιτυχώς!')
    return redirect('manage_properties')

@login_required
def delete_complex(request, complex_id):
    complex = PropertyComplex.objects.get(id=complex_id)
    complex.delete()
    messages.success(request, 'Το συγκρότημα ακινήτων διαγράφηκε επιτυχώς!')
    return redirect('manage_properties')

@login_required
def delete_unit(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    unit.delete()
    messages.success(request, 'Η μονάδα διαγράφηκε επιτυχώς!')
    return redirect('manage_properties')

@login_required
def delete_lease(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    lease.property.status = 'available'
    lease.property.save()
    lease.delete()
    messages.success(request, 'Η μίσθωση διαγράφηκε επιτυχώς!')
    return redirect('manage_properties')

@login_required
def payment_status(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    if lease.monthly_payment_status.lower() == 'pending':
        lease.pay()
        messages.success(request, 'Η πληρωμή σημειώθηκε ως εξοφλημένη επιτυχώς!')
    else:
        messages.info(request, 'Payment is already marked as paid.')
    return redirect('manage_properties')

@login_required
def finances(request):
    update_status(request)
    # Get leases for both properties and units owned by the user
    property_leases = Lease.objects.filter(property__owner=request.user)
    unit_leases = Lease.objects.filter(unit__owner=request.user)
    leases = property_leases.union(unit_leases)
    notifications = Message.objects.filter(owner=request.user).order_by('-timestamp')
    
    # Get recent expenses for the user
    recent_expenses = Expense.objects.filter(
        models.Q(property__owner=request.user) | models.Q(unit__owner=request.user)
    ).order_by('-date')[:10]  # Get last 10 expenses
    
    return render(request, 'pm/finances.html', {
        'leases': leases, 
        'notifications': notifications,
        'recent_expenses': recent_expenses
    })

@login_required
def create_expense(request):
    # Get parameters from query string
    property_type = request.GET.get('type')
    object_id = request.GET.get('id')
    
    property_obj = None
    unit_obj = None
    
    # Determine if it's a property or unit
    if property_type == 'property' and object_id:
        try:
            property_obj = Property.objects.get(id=object_id, owner=request.user)
        except Property.DoesNotExist:
            messages.error(request, 'Property not found.')
            return redirect('expenses')
    elif property_type == 'unit' and object_id:
        try:
            unit_obj = Unit.objects.get(id=object_id, owner=request.user)
        except Unit.DoesNotExist:
            messages.error(request, 'Unit not found.')
            return redirect('expenses')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            if property_obj:
                expense.property = property_obj
            elif unit_obj:
                expense.unit = unit_obj
            else:
                messages.error(request, 'No valid property or unit specified.')
                return redirect('expenses')
            expense.save()
            messages.success(request, 'Το έξοδο καταγράφηκε επιτυχώς!')
            return redirect('expenses')
        else:
            messages.error(request, 'Σφάλμα! Παρακαλώ ελέγξτε τα δεδομένα της φόρμας.')
    else:
        form = ExpenseForm()
    
    context = {
        'form': form,
        'property_obj': property_obj,
        'unit_obj': unit_obj,
        'property_type': property_type
    }
    return render(request, 'pm/create_expense.html', context)

@login_required
def expenses(request):
    # Get all properties and units owned by the user
    properties = Property.objects.filter(owner=request.user)
    units = Unit.objects.filter(owner=request.user)
    
    # Get all expenses for owned properties and units
    property_expenses = Expense.objects.filter(property__owner=request.user)
    unit_expenses = Expense.objects.filter(unit__owner=request.user)
    
    # Combine and organize data
    property_data = []
    for prop in properties:
        expenses = property_expenses.filter(property=prop).order_by('-date')
        property_data.append({
            'type': 'property',
            'object': prop,
            'expenses': expenses,
            'total_expenses': sum(exp.amount for exp in expenses)
        })
    
    for unit in units:
        expenses = unit_expenses.filter(unit=unit).order_by('-date')
        property_data.append({
            'type': 'unit',
            'object': unit,
            'expenses': expenses,
            'total_expenses': sum(exp.amount for exp in expenses)
        })
    
    return render(request, 'pm/expenses.html', {
        'property_data': property_data,
        'total_properties': len(property_data)
    })

@login_required
def submit_payment(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.lease = lease
            document.save()
            lease.pay()
            messages.success(request, 'Η πληρωμή υποβλήθηκε και σημειώθηκε ως εξοφλημένη επιτυχώς!')
            return redirect('finances')
        else:
            messages.error(request, 'Σφάλμα! Παρακαλώ βεβαιωθείτε ότι το αρχείο που ανεβάσατε είναι έγκυρο PDF.')
    else:
        form = DocumentForm()
    return render(request, 'pm/submit_payment.html', {'form':form, 'lease': lease})

@login_required
def request_payment(request):
    # Get leases for both properties and units where user is a tenant
    property_leases = Lease.objects.filter(property__isnull=False, tenant=request.user)
    unit_leases = Lease.objects.filter(unit__isnull=False, tenant=request.user)
    leases = property_leases.union(unit_leases).order_by('-created_at')
    return render(request, 'pm/request_payment.html', {'leases': leases})

@login_required
def submit_payment_request(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.lease = lease
            document.status = 'unverified'
            document.save()
            messages.success(request, 'Το αίτημα πληρωμής υποβλήθηκε επιτυχώς!')
            return redirect('home')
        else:
            messages.error(request, 'Σφάλμα! Παρακαλώ βεβαιωθείτε ότι το αρχείο που ανεβάσατε είναι έγκυρο PDF.')
    else:
        form = DocumentForm()
    return render(request, 'pm/submit_payment.html', {'form':form, 'lease': lease})

@login_required
def verify_payment(request, document_id):
    document = Document.objects.get(id=document_id)
    document.verify()
    document.save()
    lease = document.lease
    lease.pay()
    messages.success(request, 'Payment verified and marked as paid successfully!')
    return redirect('finances')

@login_required
def documents(request):
    # Get documents for both property and unit leases owned by the user
    property_documents = Document.objects.filter(lease__property__owner=request.user)
    unit_documents = Document.objects.filter(lease__unit__owner=request.user)
    
    # Separate unverified and verified documents before union
    unverified_property_docs = property_documents.filter(status='unverified')
    unverified_unit_docs = unit_documents.filter(status='unverified')
    verified_property_docs = property_documents.filter(status='verified')
    verified_unit_docs = unit_documents.filter(status='verified')
    
    # Union the filtered documents
    unverified_documents = unverified_property_docs.union(unverified_unit_docs).order_by('-uploaded_at')
    verified_documents = verified_property_docs.union(verified_unit_docs).order_by('-uploaded_at')
    
    return render(request, 'pm/documents.html', {
        'unverified_documents': unverified_documents,
        'verified_documents': verified_documents
    })