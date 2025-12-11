from django.db import models
from django.contrib.auth.models import User as AuthUser
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

# --- CATEGORY MODEL ---
class Category(models.Model):
    group = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.group

class Supplier(models.Model):
    company_name = models.CharField(max_length=100, default="Generic Supplier")
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.company_name

# --- MAIN STOCK MODEL ---
class Stock(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Quantities
    quantity = models.IntegerField(default='0', blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)
    
    # Reorder Level
    re_order = models.IntegerField(default='0', blank=True, null=True)

    # Tracking Details
    received_by = models.CharField(max_length=50, blank=True, null=True)
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    issued_to = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    date = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    
    export_to_csv = models.BooleanField(default=False)
    
    # Product Image
    image = models.ImageField(upload_to='img', null=True, blank=True)
    
    # Automated QR Code Field
    qr_code = models.ImageField(upload_to='qr_codes', blank=True, null=True)

    def __str__(self):
        return str(self.item_name)

    def save(self, *args, **kwargs):
        # 1. If this is a new item (no ID), save it first to get an ID
        if not self.id:
            super().save(*args, **kwargs)

        # 2. If no QR code exists, generate one
        if not self.qr_code and self.id:
            # The data we want to encode
            qr_data = f"/stock_detail/{self.id}/"
            
            # Generate the QR Code Image
            qrcode_img = qrcode.make(qr_data)
            
            # Resize and paste logic
            canvas = Image.new('RGB', (290, 290), 'white')
            qrcode_img = qrcode_img.resize((290, 290))
            canvas.paste(qrcode_img, (0, 0))
            
            # Save to buffer
            fname = f'qr_code-{self.id}.png'
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            
            # Save to the field without triggering a full save yet
            self.qr_code.save(fname, File(buffer), save=False)
            
            # CRITICAL FIX: Remove 'force_insert' if it exists.
            # This ensures the second save is an UPDATE, not an INSERT.
            kwargs.pop('force_insert', None)
            
            super().save(*args, **kwargs)
            
        elif self.id:
            # If it's a standard update (changing quantity, etc), just save normally
            # But prevent double-saving if we just created it in step 1
            if 'force_insert' not in kwargs:
                super().save(*args, **kwargs)

# --- STOCK HISTORY MODEL ---
class StockHistory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    received_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    issued_to = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    re_order = models.IntegerField(default='0', blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    date = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)


# --- AUXILIARY MODELS ---
class User(models.Model):
    user = models.TextField(default=None)
    def __str__(self): return self.user

class Country(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self): return self.name

class Person(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self): return self.name

class Scrums(models.Model):
    task = models.CharField(max_length=100, blank=True, null=True)
    task_description = models.CharField(max_length=100, blank=True, null=True)
    task_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    def __str__(self): return self.task

class ScrumTitles(models.Model):
    lists = models.CharField(max_length=150, blank=True, null=True)
    def __str__(self): return str(self.lists)

class Contacts(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='img', null=True, blank=True)
    def __str__(self): return str(self.name)