from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Property, Lease, Problem, Message, Document, PropertyComplex, Unit
from .forms import NewPropertyForm, NewLeaseForm, NewProblemForm, AddTenantForm, DocumentForm, NewPropertyComplexForm, NewUnitForm

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
    problems = Problem.objects.filter(property__owner=request.user).order_by('-created_at')
    notifications = Message.objects.filter(owner=request.user).order_by('-timestamp')
    update_status(request)
    return render(request, 'pm/home.html', {'problems':problems, 'notifications':notifications})

@login_required
def create_property_complex(request):
    if request.method == 'POST':
        form = NewPropertyComplexForm(request.POST)
        if form.is_valid():
            property_complex = form.save(commit=False)
            property_complex.owner = request.user
            property_complex.save()
            messages.success(request, 'Property Complex created successfully!')
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
            messages.success(request, 'Unit added successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error! Invalid data provided.')
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
            messages.success(request, 'Property added successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error! Invalid data provided.')
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
        form = NewLeaseForm(request.POST)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.property = property
            lease.save()
            form.save_m2m()
            property.status = 'rented'
            property.save()
            messages.success(request, 'Lease created successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewLeaseForm()
    return render(request, 'pm/create_lease.html', {'form': form})

@login_required
def create_lease_unit(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST)
        if form.is_valid():
            lease = form.save(commit=False)
            lease.unit = unit
            lease.save()
            form.save_m2m()
            unit.status = 'rented'
            unit.save()
            messages.success(request, 'Lease created successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewLeaseForm()
    return render(request, 'pm/create_lease.html', {'form': form, 'unit': unit})

@login_required
def report_problem(request):
    if request.method == 'POST':
        form = NewProblemForm(request.POST, tenant=request.user)
        if form.is_valid():
            problem = form.save(commit=False)
            problem.tenant = request.user
            problem.save()
            messages.success(request, 'Problem reported successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewProblemForm(tenant=request.user)
    return render(request, 'pm/report_problem.html', {'form': form})

@login_required
def solve_problem(request, problem_id):
    problem = Problem.objects.get(id=problem_id)
    problem.delete()
    messages.success(request, 'Problem marked as solved successfully!') #Femboy Spelling Correction
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
    messages.success(request, 'Tennant removed successfully!')
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
            messages.success(request, 'Tennant added successfully!')
            return redirect(f'/create_lease/{property_id}/?tenants={",".join(map(str, tenant_ids))}')
        else:
            messages.error(request, 'Error!')
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
            messages.success(request, 'Property updated successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
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
            messages.success(request, 'Unit updated successfully!')
            return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewUnitForm(instance=unit)
    return render(request, 'pm/manage_unit.html', {'form': form, 'unit': unit, 'lease': lease})

@login_required
def edit_lease(request, property_id):
    update_status(request)
    lease = Lease.objects.get(property__id=property_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, instance=lease)
        if form.is_valid():
            l = form.save(commit=False)
            if l.tenant.count() == 0:
                messages.error(request, 'Lease must have at least one tenant!')
            else:
                form.save()
                messages.success(request, 'Lease updated successfully!')
                return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewLeaseForm(instance=lease)
    return render(request, 'pm/edit_lease.html', {'form': form, 'lease': lease})

@login_required
def edit_lease_unit(request, unit_id):
    update_status(request)
    lease = Lease.objects.get(unit__id=unit_id)
    if request.method == 'POST':
        form = NewLeaseForm(request.POST, instance=lease)
        if form.is_valid():
            l = form.save(commit=False)
            if l.tenant.count() == 0:
                messages.error(request, 'Lease must have at least one tenant!')
            else:
                form.save()
                messages.success(request, 'Lease updated successfully!')
                return redirect('manage_properties')
        else:
            messages.error(request, 'Error!')
    else:
        form = NewLeaseForm(instance=lease)
    return render(request, 'pm/edit_lease.html', {'form': form, 'lease': lease})

@login_required
def delete_property(request, property_id):
    property = Property.objects.get(id=property_id)
    property.delete()
    messages.success(request, 'Property deleted successfully!')
    return redirect('manage_properties')

@login_required
def delete_complex(request, complex_id):
    complex = PropertyComplex.objects.get(id=complex_id)
    complex.delete()
    messages.success(request, 'Property Complex deleted successfully!')
    return redirect('manage_properties')

@login_required
def delete_unit(request, unit_id):
    unit = Unit.objects.get(id=unit_id)
    unit.delete()
    messages.success(request, 'Unit deleted successfully!')
    return redirect('manage_properties')

@login_required
def delete_lease(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    lease.property.status = 'available'
    lease.property.save()
    lease.delete()
    messages.success(request, 'Lease deleted successfully!')
    return redirect('manage_properties')

@login_required
def payment_status(request, lease_id):
    lease = Lease.objects.get(id=lease_id)
    if lease.monthly_payment_status.lower() == 'pending':
        lease.pay()
        messages.success(request, 'Payment marked as paid successfully!')
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
    return render(request, 'pm/finances.html', {'leases':leases, 'notifications':notifications})

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
            messages.success(request, 'Payment submitted and marked as paid successfully!')
            return redirect('finances')
        else:
            messages.error(request, 'Error! Please ensure the uploaded file is a valid PDF.')
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
            messages.success(request, 'Payment request submitted successfully!')
            return redirect('finances')
        else:
            messages.error(request, 'Error! Please ensure the uploaded file is a valid PDF.')
    else:
        form = DocumentForm()
    return render(request, 'pm/submit_payment.html', {'form':form, 'lease': lease})

@login_required
def verify_payment(request, document_id):
    document = Document.objects.get(id=document_id)
    document.status = 'verified'
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