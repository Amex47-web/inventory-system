import csv
import os
from django.conf import settings
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .form import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.functions import Coalesce
from django.db.models import Sum, F, FloatField
from datetime import timedelta
from django.utils import timezone
import pandas as pd
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.contrib import messages
# Ensure you have these:
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.units import inch
import io

from django.contrib.auth.decorators import login_required, permission_required

# --- HELPER FUNCTIONS ---

def perform_abc_analysis(queryset):
    """
    Classifies inventory into A (Top 20%), B (Next 30%), C (Bottom 50%)
    based on Quantity. (In a real app, use Quantity * Unit Cost).
    """
    # Sort items by quantity (descending)
    sorted_stock = queryset.order_by('-quantity')
    total_stock = sorted_stock.count()
    
    a_limit = int(total_stock * 0.2) # Top 20%
    b_limit = int(total_stock * 0.5) # Next 30% (accumulated 50%)
    
    a_items = sorted_stock[:a_limit]
    b_items = sorted_stock[a_limit:b_limit]
    c_items = sorted_stock[b_limit:]
    
    return {
        'A': a_items.count(), 
        'B': b_items.count(), 
        'C': c_items.count(),
        'A_list': a_items, # To show in tables if needed
    }

# --- VIEWS ---

def new_register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login/')
    context = {'form': form}
    return render(request, 'stock/register.html', context)



@login_required
def get_client_ip(request):
    """
    DASHBOARD VIEW
    Includes: IP Tracking, ABC Analysis, Low Stock Alerts, Charts, and Financial Analytics.
    """
    # 1. IP Tracking Logic
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Save user IP log if unique
    if not User.objects.filter(user__icontains=ip).exists():
        u = User(user=ip)
        u.save()

    # 2. Fetch Data
    queryset = Stock.objects.all()
    categories = Category.objects.all()

    # 3. Chart Data Preparation
    label_item = [stock.item_name for stock in queryset]
    data = [stock.quantity for stock in queryset]
    issue_data = [stock.issue_quantity for stock in queryset]
    receive_data = [stock.receive_quantity for stock in queryset]
    
    labels = [str(cat.group) for cat in categories] # For Pie Chart

    # 4. KPI Counters
    count = User.objects.all().count() # Visitor Count
    total_items = queryset.count()
    total_quantity = queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # --- 5. FINANCIAL ANALYTICS (NEW) ---
    # Calculate Total Inventory Value: Sum of (Quantity * Unit Price) for all items
    total_value = queryset.aggregate(
        total=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
    )['total']
    
    # Handle case where DB is empty or prices are missing (returns None)
    if total_value is None:
        total_value = 0

    # 6. DATA DRIVEN: Low Stock Alerts
    # Find items where quantity is less than or equal to reorder level
    low_stock_items = queryset.filter(quantity__lte=F('re_order'))

    # 7. DATA DRIVEN: ABC Analysis
    abc_data = perform_abc_analysis(queryset)

    context = {
        'count': count,
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_value': round(total_value, 2), # New Context Variable
        'labels': labels, # Category Names
        'data': data, # Current Quantity
        'issue_data': issue_data,
        'receive_data': receive_data,
        'label_item': label_item, # Item Names
        'low_stock_items': low_stock_items, # ALERT DATA
        'abc': abc_data, # ABC ANALYSIS DATA
    }
    return render(request, 'stock/home.html', context)


@login_required
def view_stock(request):
    title = "VIEW STOCKS"
    everything = Stock.objects.all()
    form = StockSearchForm(request.POST or None)

    # Search Logic
    if request.method == 'POST':
        category = form['category'].value()
        everything = Stock.objects.filter(item_name__icontains=form['item_name'].value())
        
        if category != '':
            everything = everything.filter(category_id=category)

        # Export to CSV Logic
        if form['export_to_CSV'].value() == True:
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename = "Inventory_Report.csv"'
            writer = csv.writer(resp)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY', 'REORDER LEVEL'])
            for stock in everything:
                writer.writerow([stock.category, stock.item_name, stock.quantity, stock.re_order])
            return resp

    context = {'title': title, 'everything': everything, 'form': form}
    return render(request, 'stock/view_stock.html', context)


@login_required
def scrum_list(request):
    title = 'Add List'
    add = ScrumTitles.objects.all()
    sub = Scrums.objects.all()
    
    form = AddScrumListForm(prefix='banned')
    task_form = AddScrumTaskForm(prefix='expected')

    if request.method == 'POST':
        if 'banned' in request.POST: # Check which form was submitted
             form = AddScrumListForm(request.POST, prefix='banned')
             if form.is_valid():
                 form.save()
                 return redirect('/scrum_board') # Redirect to clear post data
        
        if 'expected' in request.POST:
            task_form = AddScrumTaskForm(request.POST, prefix='expected')
            if task_form.is_valid():
                task_form.save()
                return redirect('/scrum_board')

    context = {'add': add, 'form': form, 'task_form': task_form, 'sub': sub, 'title': title}
    return render(request, 'stock/scrumboard.html', context)


@login_required
def scrum_view(request):
    title = 'View'
    viewers = ScrumTitles.objects.all()
    context = {'title': title, 'view': viewers}
    return render(request, 'stock/scrumboard.html', context)


@login_required
@permission_required('stock.add_stock', raise_exception=True) # <--- Only Managers
def add_stock(request):
    title = 'Add Stock'
    add = Stock.objects.all()
    form = StockCreateForm()
    if request.method == 'POST':
        form = StockCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item Successfully Added')
            return redirect('/view_stock')
    context = {'add': add, 'form': form, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
def update_stock(request, pk):
    title = 'Update Stock'
    update = get_object_or_404(Stock, id=pk)
    form = StockUpdateForm(instance=update)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            # Handle Image Replacement safely
            if update.image and hasattr(update.image, 'path') and os.path.exists(update.image.path):
                 # Optional: Only delete if a new image is actually uploaded
                 # os.remove(update.image.path) 
                 pass
            form.save()
            messages.success(request, 'Successfully Updated!')
            return redirect('/view_stock')
    context = {'form': form, 'update': update, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
@permission_required('stock.delete_stock', raise_exception=True) # <--- Only Managers
def delete_stock(request, pk):
    item = get_object_or_404(Stock, id=pk)
    item.delete()
    messages.success(request, 'Item has been deleted.')
    return redirect('/view_stock')


@login_required
def stock_detail(request, pk):
    detail = get_object_or_404(Stock, id=pk)
    
    # --- 1. PREDICTIVE ANALYTICS LOGIC ---
    # Get history for the last 30 days
    last_month = timezone.now() - timedelta(days=30)
    history = StockHistory.objects.filter(item_name=detail.item_name, timestamp__gte=last_month)
    
    # Calculate total issued quantity (Outflow)
    total_issued = sum([item.issue_quantity for item in history if item.issue_quantity > 0])
    
    # Calculate Daily Average Consumption (Burn Rate)
    # Avoid division by zero
    if total_issued > 0:
        daily_avg_burn = total_issued / 30
        days_remaining = detail.quantity / daily_avg_burn
    else:
        daily_avg_burn = 0
        days_remaining = 999 # Infinite/Safe

    # --- 2. HISTORICAL GRAPH DATA ---
    # Fetch history for this specific item, ordered by time
    graph_qs = StockHistory.objects.filter(item_name=detail.item_name).order_by('timestamp')
    
    # Prepare lists for Chart.js (Dates on X-axis, Quantity on Y-axis)
    # Formatted as strings to pass to the template safely
    dates = [obj.timestamp.strftime('%Y-%m-%d %H:%M') for obj in graph_qs if obj.timestamp] 
    quantities = [obj.quantity for obj in graph_qs]

    context = {
        'detail': detail,
        'daily_burn': round(daily_avg_burn, 2),
        'days_remaining': int(days_remaining),
        'dates': dates,        # Data for X-Axis
        'quantities': quantities # Data for Y-Axis
    }
    
    return render(request, 'stock/stock_detail.html', context)


@login_required
def issue_item(request, pk):
    issue = get_object_or_404(Stock, id=pk)
    form = IssueForm(request.POST or None, instance=issue)
    if form.is_valid():
        value = form.save(commit=False)
        # Ensure we don't overwrite receive quantity
        value.receive_quantity = 0 
        
        # Calculate new quantity
        value.quantity = value.quantity - value.issue_quantity
        value.issued_by = str(request.user)
        
        if value.quantity >= 0:
            value.save()
            messages.success(request, f"Issued Successfully. {value.quantity} {value.item_name}s remaining.")
        else:
            messages.error(request, f"Insufficient Stock! You only have {issue.quantity}.")
            return redirect('/stock_detail/' + str(value.id))

        return redirect('/stock_detail/' + str(value.id))

    context = {
        "title": 'Issue ' + str(issue.item_name),
        "issue": issue,
        "form": form,
        "username": 'Issued by: ' + str(request.user),
    }
    return render(request, "stock/add_stock.html", context)


@login_required
def receive_item(request, pk):
    receive = get_object_or_404(Stock, id=pk)
    form = ReceiveForm(request.POST or None, instance=receive)
    if form.is_valid():
        value = form.save(commit=False)
        value.issue_quantity = 0
        value.quantity = value.quantity + value.receive_quantity
        value.received_by = str(request.user)
        value.save()
        messages.success(request, f"Received Successfully. {value.quantity} {value.item_name}s now in Store.")

        return redirect('/stock_detail/' + str(value.id))
    context = {
        "title": 'Receive ' + str(receive.item_name),
        "receive": receive,
        "form": form,
        "username": 'Received by: ' + str(request.user),
    }
    return render(request, "stock/add_stock.html", context)


@login_required
def re_order(request, pk):
    order = get_object_or_404(Stock, id=pk)
    form = ReorderLevelForm(request.POST or None, instance=order)
    if form.is_valid():
        value = form.save(commit=False)
        value.save()
        messages.success(request, 'Reorder level updated.')
        return redirect('/view_stock')
    context = {
        'value': order,
        'form': form
    }
    return render(request, 'stock/add_stock.html', context)


@login_required()
def view_history(request):
    title = "STOCK HISTORY"
    history = StockHistory.objects.all()
    form = StockHistorySearchForm(request.POST or None)
    
    if request.method == 'POST':
        category = form['category'].value()
        # Filter by name and date range
        history = StockHistory.objects.filter(
            item_name__icontains=form['item_name'].value(),
            last_updated__range=[form['start_date'].value(), form['end_date'].value()]
        )
        if category != '':
            history = history.filter(category_id=category)

        # Export History CSV
        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock_History.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY','ITEM NAME','QUANTITY','ISSUE QTY','RECEIVE QTY','RECEIVED BY','ISSUED BY','LAST UPDATED'])
            for stock in history:
                writer.writerow([stock.category, stock.item_name, stock.quantity, stock.issue_quantity, stock.receive_quantity, stock.received_by, stock.issued_by, stock.last_updated])
            return response
            
    context = {
        'title': title,
        'history': history,
        'form': form
    }
    return render(request, 'stock/view_history.html', context)


@login_required
def dependent_forms(request):
    title = 'Dependent Forms'
    form = DependentDropdownForm()
    if request.method == 'POST':
        form = DependentDropdownForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Added!')
            return redirect('/depend_form_view')
    context = {'form': form, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
def dependent_forms_update(request, pk):
    title = 'Update Form'
    dependent_update = get_object_or_404(Person, id=pk)
    form = DependentDropdownForm(instance=dependent_update)
    if request.method == 'POST':
        form = DependentDropdownForm(request.POST, instance=dependent_update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Updated!')
            return redirect('/depend_form_view')
    context = {
        'title': title,
        'dependent_update': dependent_update,
        'form': form
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def dependent_forms_view(request):
    title = 'Dependent Views'
    viewers = Person.objects.all()
    context = {'title': title, 'view': viewers}
    return render(request, 'stock/depend_form_view.html', context)


@login_required
def delete_dependant(request, pk):
    get_object_or_404(Person, id=pk).delete()
    messages.success(request, 'Deleted successfully.')
    return redirect('/depend_form_view')


def load_stats(request):
    country_idm = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_idm)
    return render(request, 'stock/state_dropdown_list_options.html', {'states': states})


def load_cities(request):
    state_main_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_main_id)
    return render(request, 'stock/city_dropdown_list_options.html', {'cities': cities})


@login_required
def contact(request):
    title = 'Contacts'
    people = Contacts.objects.all()
    form = ContactsForm(request.POST or None)
    if request.method == 'POST':
        form = ContactsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully Added')
            return redirect('/contacts')
    context = {'people': people, 'form': form, 'title': title}
    return render(request, 'stock/contacts.html', context)

@login_required
def generate_pdf(request, pk):
    # 1. Get the stock item
    stock = get_object_or_404(Stock, id=pk)
    
    # 2. Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # 3. Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- HEADER ---
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, height - 50, "PURCHASE ORDER")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 80, "Generated By: Inventory Management System")
    p.drawString(50, height - 95, f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    p.drawString(width - 250, height - 50, "PO Number: #PO-" + str(stock.id) + "-001")

    # Draw a line
    p.setLineWidth(1)
    p.line(50, height - 110, width - 50, height - 110)

    # --- VENDOR INFO (DYNAMIC) ---
    # This section now pulls data from the Supplier model if it exists
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 140, "TO VENDOR:")
    p.setFont("Helvetica", 12)
    
    # Check if a supplier is linked to this item
    if hasattr(stock, 'supplier') and stock.supplier:
        p.drawString(50, height - 155, str(stock.supplier.company_name))
        
        # Handle address and contact details
        current_y = height - 170
        if stock.supplier.address:
            p.drawString(50, current_y, str(stock.supplier.address))
            current_y -= 15
        
        if stock.supplier.email:
            p.drawString(50, current_y, f"Email: {stock.supplier.email}")
            current_y -= 15
            
        if stock.supplier.phone:
            p.drawString(50, current_y, f"Phone: {stock.supplier.phone}")
            
    else:
        # Fallback if no supplier is assigned
        p.setFillColor(colors.red)
        p.drawString(50, height - 155, "NO SUPPLIER ASSIGNED")
        p.setFillColor(colors.black) # Reset color

    # --- ITEM TABLE HEADER ---
    y_start = height - 230
    p.setFillColor(colors.lightgrey)
    p.rect(50, y_start, width - 100, 20, fill=1) # Gray background for header
    p.setFillColor(colors.black)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y_start + 6, "Item Name")
    p.drawString(300, y_start + 6, "Category")
    p.drawString(450, y_start + 6, "Qty Required")

    # --- ITEM ROW CALCULATION ---
    # Smart Logic: 
    # 1. If Reorder Level is set (>0), try to buy enough to reach 3x that level (Safety Stock).
    # 2. If Reorder Level is 0, assume we need a standard batch of 50.
    
    if stock.re_order and stock.re_order > 0:
        target_stock = stock.re_order * 3
        suggested_order = target_stock - stock.quantity
    else:
        # Fallback if no reorder level is set
        suggested_order = 50

    # Ensure we never order 0 or negative amounts
    # (Minimum order quantity = 10)
    if suggested_order < 10:
        suggested_order = 10

    # --- DRAW ITEM ROW ---
    y_row = y_start - 25
    p.setFont("Helvetica", 12)
    p.drawString(60, y_row, str(stock.item_name))
    p.drawString(300, y_row, str(stock.category))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(450, y_row, str(suggested_order) + " units")

    # Draw a line below row
    p.line(50, y_row - 10, width - 50, y_row - 10)

    # --- FOOTER ---
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "This is a computer-generated document. No signature required.")

    # 4. Close the PDF object cleanly
    p.showPage()
    p.save()

    # 5. FileResponse sets the Content-Disposition header
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'PO_{stock.item_name}.pdf')


@login_required
def upload_csv(request):
    if request.method == 'POST':
        try:
            # 1. Check if a file was uploaded
            if 'csv_file' not in request.FILES:
                messages.error(request, "No file selected")
                return redirect('upload_csv')

            csv_file = request.FILES['csv_file']

            # 2. Check if it is actually a CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File is not CSV type')
                return redirect('upload_csv')

            # 3. Read the file using Pandas
            df = pd.read_csv(csv_file)
            
            # --- FIX: CLEAN HEADERS ---
            # Remove any leading/trailing spaces from column names (e.g. "Category " -> "Category")
            df.columns = df.columns.str.strip()
            
            # Check if required columns exist BEFORE processing
            required_cols = ['Category', 'Item Name', 'Quantity', 'Reorder Level']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                messages.error(request, f"Missing columns in CSV: {', '.join(missing_cols)}")
                return redirect('upload_csv')

            # 4. Iterate over the rows
            success_count = 0
            for index, row in df.iterrows():
                # Get or Create the Category (Foreign Key logic)
                category_name = str(row['Category']).strip() # Clean data too
                category_obj, created = Category.objects.get_or_create(group=category_name)

                # Create the Stock Item
                Stock.objects.create(
                    category=category_obj,
                    item_name=str(row['Item Name']).strip(),
                    quantity=int(row['Quantity']),
                    re_order=int(row['Reorder Level'])
                )
                success_count += 1
            
            messages.success(request, f'Successfully imported {success_count} items!')
            return redirect('view_stock')

        except Exception as e:
            # Print error to terminal for debugging
            print(f"CSV Error: {e}")
            messages.error(request, f"Error processing file: {e}")
            return redirect('upload_csv')

    return render(request, 'stock/upload_csv.html')

def custom_logout(request):
    logout(request)
    # Redirect to login page after logout
    return redirect('/accounts/login/')



# --- SHOPPING CART LOGIC ---

@login_required
def add_to_cart(request, pk):
    # 1. Get the item
    item = get_object_or_404(Stock, id=pk)
    
    # 2. Get the Cart from session (or create empty dict)
    cart = request.session.get('cart', {})
    
    # 3. Add item to cart (Default quantity 1)
    # We store: { 'item_id': quantity }
    item_id = str(pk)
    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1
        
    # 4. Save back to session
    request.session['cart'] = cart
    
    messages.success(request, f"Added {item.item_name} to Issue Cart")
    return redirect('view_stock')

@login_required
def view_cart(request):
    # 1. Get cart data
    cart = request.session.get('cart', {})
    
    # 2. Fetch actual objects from DB to show names/prices
    cart_items = []
    total_items_count = 0
    
    for item_id, quantity in cart.items():
        stock = Stock.objects.get(id=item_id)
        cart_items.append({
            'product': stock,
            'quantity': quantity,
            'total_available': stock.quantity
        })
        total_items_count += quantity
        
    context = {
        'cart_items': cart_items,
        'total_count': total_items_count
    }
    return render(request, 'stock/cart.html', context)

@login_required
def clear_cart(request):
    # Delete the session variable
    if 'cart' in request.session:
        del request.session['cart']
    messages.info(request, "Cart Cleared")
    return redirect('view_cart')

@login_required
def checkout_cart(request):
    # 1. Get Cart
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, "Cart is empty")
        return redirect('view_cart')
        
    # 2. Process Each Item
    for item_id, issue_qty in cart.items():
        stock = Stock.objects.get(id=item_id)
        
        # Check stock levels
        if stock.quantity >= issue_qty:
            stock.quantity -= issue_qty
            stock.issue_quantity += issue_qty
            stock.save() # This triggers your history signal automatically!
        else:
            messages.warning(request, f"Skipped {stock.item_name}: Not enough stock (Req: {issue_qty}, Has: {stock.quantity})")
            
    # 3. Clear Cart and Finish
    del request.session['cart']
    messages.success(request, "Bulk Issue Completed Successfully!")
    return redirect('view_stock')