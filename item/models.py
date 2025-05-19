from asyncio.windows_events import NULL
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Category Model
class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.name}"

# Item Model
class Item(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='items', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='Item_Images')
    availability = models.CharField(default='All Week',max_length=100)
    inHold = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE, default=1)
    extras = models.ManyToManyField('Extra', blank=True, related_name='items') 

    def __str__(self):
        return self.name

# Staff Model
class Staff(models.Model):
    ROLE_CHOICES = [
        ('chef', 'Chef'),
        ('waiter', 'Waiter'), 
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('cleaner', 'Cleaner'),
        ('barista', 'Barista'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    hire_date = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loan = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Track employment status
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"


# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    loyalty_points = models.IntegerField(default=0)
    inHold = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

# OrderStatus Model
class OrderStatus(models.Model):
    statues=[    ('readytoprint', 'Ready to Print'),
        ('printed', 'Printed'),
         ('printing', 'Printing'),
        ('completed','Completed'),('pending','Pending'),('delivered','Delivered'),('served','Served')]
    name = models.CharField(max_length=100,choices=statues,default='readytoprint')
    description = models.TextField(null=True, blank=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    class Meta:

      verbose_name_plural = 'Order Status'      



# Table Model
class Table(models.Model):
    TABLE_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance')
    ]
    
    number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=TABLE_STATUS_CHOICES, default='available')
    qr_code = models.ImageField(upload_to='table_qr_codes/', null=True, blank=True)
    section = models.CharField(max_length=50, default='Main',null=True,blank=True)  # e.g., Main, Outdoor, VIP
    is_active = models.BooleanField(default=True)
    inHold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.id}  {self.number} ({self.get_status_display()})"

    class Meta:
        ordering = ['number']  

# Order Model
class Order(models.Model):


    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True, blank=True)
    ordered_at = models.DateTimeField(default=timezone.now)
    printed_at = models.DateTimeField(default=timezone.now)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    served_at = models.DateTimeField(null=True, blank=True)
    delivery_address = models.TextField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    special_instructions = models.TextField(null=True, blank=True)
    inHold = models.BooleanField(default=False)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    table_number = models.CharField(default='Take Away', max_length=50)
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    def calculate_total_amount(self):
        if not self.pk:
            return 0
        else:
        # Calculate the total by summing up all the OrderItem prices
            return sum(item.price for item in self.orderitem_set.all())

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)
        # for item_order in self.orderitem_set.all():
        #     print("Order save loop: Saving item order", item_order)
        #     item_order.save() 
        #     print("Order save loop: Finished saving item order", item_order)
        # self.total_amount = self.calculate_total_amount()
        # print("Order total amount calculated:", self.total_amount)
        # super().save(update_fields=["total_amount"])
        
      

    def __str__(self):
        return f"Order {self.id}"
        # return f"Order {self.id} - {self.customer.name}"
    

# Extra Model
class Extra(models.Model):
    name= models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customizations = models.TextField(null=True, blank=True)  # Optional customizations for the item
    selected_extras = models.ManyToManyField(Extra, blank=True)
    inHold = models.BooleanField(default=False)

    def calculate_total_price(self):
      base_price = self.item.price * self.quantity
      extras_price = sum(extra.calculate_price() for extra in self.orderitemextra_set.all())
      return base_price + extras_price
        

    def save(self, *args, **kwargs):

    # Set the price initially before saving
      if not self.price:  # If the price is not set yet
        self.price = self.item.price * self.quantity   
      super().save(*args, **kwargs)
    
      if self.pk:
        self.price = self.calculate_total_price()
      super().save(*args, update_fields=['price'])

      # I disabled this lines because I think they are duplicated and If things got wrong please when trying to calculate the orderitem price  remmber that those line were not commented 
    # # Now calculate total price with extras after the object has been saved
    #   self.price = self.calculate_total_price()  # Recalculate price including extras
   
    # # Save again to update the price field
    #   super().save(*args, update_fields=['price'])

 
       

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"    

# Inventory Model
class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_quantity = models.IntegerField(null=True, blank=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name

# Supplier Model
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Reservation Model
class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    reservation_date = models.DateTimeField()
    number_of_guests = models.IntegerField()
    status = models.CharField(max_length=100)  # 'confirmed', 'canceled'
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Reservation for {self.number_of_guests} on {self.reservation_date}"

# Discount Model
class Discount(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Discount {self.discount_code} for Order {self.order.id}"

# DeliveryDetail Model
class DeliveryDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    delivery_status = models.CharField(max_length=100)  # e.g., 'pending', 'delivered'
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    inHold = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery for Order {self.order.id}"
    

class OrderItemExtra(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    extra = models.ForeignKey(Extra, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def calculate_price(self):
        return self.extra.price * self.quantity    

# # ExtraItems Model
# class ExtraItem(models.Model):
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     Extra = models.ForeignKey(Extra,on_delete=models.CASCADE)
#     inHold = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.Extra} x {self.item.name}"


class Invoice(models.Model):
    INVOICE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    table = models.ForeignKey('Table', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Invoice #{self.id} for Table {self.table.number}"  