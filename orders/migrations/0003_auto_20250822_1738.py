# orders/migrations/00XX_data_migration.py (Replace 00XX with the actual migration number)

from django.db import migrations
from django.db.models import F
from decimal import Decimal # Import Decimal for default values if needed
from django.utils import timezone # Import timezone for default=timezone.now

# --- Migration Functions for Menu App Models ---
def migrate_menu_category_data(apps, schema_editor):
    OldCategory = apps.get_model('item', 'Category')
    NewCategory = apps.get_model('menu', 'Category')

    print("Migrating Category data...")
    for old_cat in OldCategory.objects.all():
        NewCategory.objects.create(
            id=old_cat.id,
            name=old_cat.name,
            description=getattr(old_cat, 'description', ''),
            inHold=getattr(old_cat, 'inHold', False),
        )
    print("Finished migrating Category data.")

def migrate_menu_extra_data(apps, schema_editor):
    OldExtra = apps.get_model('item', 'Extra')
    NewExtra = apps.get_model('menu', 'Extra')

    print("Migrating Extra data...")
    for old_extra in OldExtra.objects.all():
        NewExtra.objects.create(
            id=old_extra.id,
            name=old_extra.name,
            price=old_extra.price,
            inHold=getattr(old_extra, 'inHold', False),
        )
    print("Finished migrating Extra data.")

def migrate_menu_item_data(apps, schema_editor):
    OldItem = apps.get_model('item', 'Item')
    NewItem = apps.get_model('menu', 'Item')
    NewCategory = apps.get_model('menu', 'Category')
    User = apps.get_model('auth', 'User') # Assuming User is Django's built-in User model

    print("Migrating Item data...")
    for old_item in OldItem.objects.all():
        category_instance = None
        if old_item.category_id:
            try:
                category_instance = NewCategory.objects.get(id=old_item.category_id)
            except NewCategory.DoesNotExist:
                print(f"Warning: Category with id {old_item.category_id} for old item {old_item.id} not found. Setting category to None.")

        created_by_user = None
        if old_item.created_by_id:
            try:
                created_by_user = User.objects.get(id=old_item.created_by_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_item.created_by_id} for old item {old_item.id} not found. Setting created_by to None.")


        NewItem.objects.create(
            id=old_item.id,
            name=old_item.name,
            category=category_instance,
            price=old_item.price,
            description=getattr(old_item, 'description', ''),
            image=getattr(old_item, 'image', ''), # ImageField needs default path or leave blank
            availability=getattr(old_item, 'availability', 'All Week'),
            inHold=getattr(old_item, 'inHold', False),
            created_at=getattr(old_item, 'created_at', timezone.now()),
            created_by=created_by_user,
        )
    print("Finished migrating Item data.")

def migrate_menu_item_extras_data(apps, schema_editor):
    # This migration handles the ManyToMany relationship between Item and Extra.
    # It assumes the old relationship was handled directly on the Item model via 'extras' M2M field.
    OldItem = apps.get_model('item', 'Item')
    NewItem = apps.get_model('menu', 'Item')
    NewExtra = apps.get_model('menu', 'Extra')

    print("Migrating Item_extras data...")
    for old_item in OldItem.objects.all():
        try:
            new_item_instance = NewItem.objects.get(id=old_item.id)
            for old_extra in old_item.extras.all():
                try:
                    new_extra_instance = NewExtra.objects.get(id=old_extra.id)
                    new_item_instance.extras.add(new_extra_instance)
                except NewExtra.DoesNotExist:
                    print(f"Warning: Extra with id {old_extra.id} not found for new item {new_item_instance.id}.")
        except NewItem.DoesNotExist:
            print(f"Warning: New Item with id {old_item.id} not found for migrating extras.")
    print("Finished migrating Item_extras data.")


# --- Migration Functions for Staff App Models (now in users app) ---
def migrate_staff_staff_data(apps, schema_editor):
    OldStaff = apps.get_model('item', 'Staff')
    NewStaff = apps.get_model('users', 'Staff') # Corrected: Assuming new 'Staff' model is in 'users' app
    User = apps.get_model('auth', 'User')

    print("Migrating Staff data...")
    for old_staff in OldStaff.objects.all():
        user_instance = None
        if old_staff.user_id:
            try:
                user_instance = User.objects.get(id=old_staff.user_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_staff.user_id} for old staff {old_staff.id} not found. Setting user to None.")

        NewStaff.objects.create(
            id=old_staff.id,
            user=user_instance,
            role=old_staff.role,
            phone_number=getattr(old_staff, 'phone_number', ''),
            hire_date=getattr(old_staff, 'hire_date', timezone.now().date()),
            salary=getattr(old_staff, 'salary', Decimal('0.00')),
            loan=getattr(old_staff, 'loan', Decimal('0.00')),
            is_active=getattr(old_staff, 'is_active', True),
            inHold=getattr(old_staff, 'inHold', False),
        )
    print("Finished migrating Staff data.")

# --- Migration Functions for User App Models ---
def migrate_users_customer_data(apps, schema_editor):
    OldCustomer = apps.get_model('item', 'Customer')
    NewCustomer = apps.get_model('users', 'Customer')
    User = apps.get_model('auth', 'User')

    print("Migrating Customer data...")
    for old_customer in OldCustomer.objects.all():
        user_instance = None
        if old_customer.user_id:
            try:
                user_instance = User.objects.get(id=old_customer.user_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_customer.user_id} for old customer {old_customer.id} not found. Setting user to None.")

        NewCustomer.objects.create(
            id=old_customer.id,
            user=user_instance,
            address=getattr(old_customer, 'address', ''),
            phone_number=getattr(old_customer, 'phone_number', ''),
            loyalty_points=getattr(old_customer, 'loyalty_points', 0),
            inHold=getattr(old_customer, 'inHold', False),
            notes=getattr(old_customer, 'notes', ''),
        )
    print("Finished migrating Customer data.")

# --- Migration Functions for Reservations App Models ---
def migrate_reservations_table_data(apps, schema_editor):
    OldTable = apps.get_model('item', 'Table')
    NewTable = apps.get_model('reservations', 'Table')

    print("Migrating Table data...")
    for old_table in OldTable.objects.all():
        NewTable.objects.create(
            id=old_table.id,
            number=old_table.number,
            capacity=old_table.capacity,
            status=old_table.status,
            qr_code=getattr(old_table, 'qr_code', ''), # ImageField needs default path or leave blank
            section=getattr(old_table, 'section', 'Main'),
            is_active=getattr(old_table, 'is_active', True),
            inHold=getattr(old_table, 'inHold', False),
            created_at=getattr(old_table, 'created_at', timezone.now()),
            last_modified=getattr(old_table, 'last_modified', timezone.now()),
        )
    print("Finished migrating Table data.")

def migrate_reservations_reservation_data(apps, schema_editor):
    OldReservation = apps.get_model('item', 'Reservation')
    NewReservation = apps.get_model('reservations', 'Reservation')
    NewCustomer = apps.get_model('users', 'Customer')
    NewTable = apps.get_model('reservations', 'Table') # Assuming new Table model in reservations app

    print("Migrating Reservation data...")
    for old_reservation in OldReservation.objects.all():
        customer_instance = None
        if old_reservation.customer_id:
            try:
                customer_instance = NewCustomer.objects.get(id=old_reservation.customer_id)
            except NewCustomer.DoesNotExist:
                print(f"Warning: Customer with id {old_reservation.customer_id} for old reservation {old_reservation.id} not found. Setting customer to None.")

        # Assuming old Reservation didn't have a direct table FK, if it did, adjust.
        # If the new Reservation model has a ForeignKey to Table, you'll need to map it
        # based on some logic from the old reservation data. For now, setting to None.
        table_instance = None
        # You might need logic here to find the correct NewTable instance if old_reservation had a table field.
        # For example, if old_reservation.table_id existed:
        # if old_reservation.table_id:
        #     try:
        #         table_instance = NewTable.objects.get(id=old_reservation.table_id)
        #     except NewTable.DoesNotExist:
        #         print(f"Warning: Table with id {old_reservation.table_id} for old reservation {old_reservation.id} not found.")


        NewReservation.objects.create(
            id=old_reservation.id,
            customer=customer_instance,
            reservation_date=old_reservation.reservation_date,
            number_of_guests=old_reservation.number_of_guests,
            status=old_reservation.status,
            inHold=getattr(old_reservation, 'inHold', False),
            # If your new Reservation model has a 'table' field:
            # table=table_instance,
        )
    print("Finished migrating Reservation data.")

# --- Migration Functions for Orders App Models ---
def migrate_orders_orderstatus_data(apps, schema_editor):
    OldOrderStatus = apps.get_model('item', 'OrderStatus')
    NewOrderStatus = apps.get_model('orders', 'OrderStatus')

    print("Migrating OrderStatus data...")
    for old_status in OldOrderStatus.objects.all():
        NewOrderStatus.objects.create(
            id=old_status.id,
            name=old_status.name,
            description=getattr(old_status, 'description', ''),
            inHold=getattr(old_status, 'inHold', False),
        )
    print("Finished migrating OrderStatus data.")

def migrate_orders_dailyordercounter_data(apps, schema_editor):
    OldDailyOrderCounter = apps.get_model('item', 'DailyOrderCounter') # Assuming it was in item app
    NewDailyOrderCounter = apps.get_model('orders', 'DailyOrderCounter')

    print("Migrating DailyOrderCounter data...")
    for old_counter in OldDailyOrderCounter.objects.all():
        NewDailyOrderCounter.objects.create(
            id=old_counter.id, # Keep ID if unique and no conflicts
            date=old_counter.date,
            counter=old_counter.counter,
        )
    print("Finished migrating DailyOrderCounter data.")

def migrate_orders_order_data(apps, schema_editor):
    OldOrder = apps.get_model('item', 'Order')
    NewOrder = apps.get_model('orders', 'Order')
    NewCustomer = apps.get_model('users', 'Customer')
    NewOrderStatus = apps.get_model('orders', 'OrderStatus')
    NewTable = apps.get_model('reservations', 'Table') # Assuming new Table model is in reservations app
    NewStaff = apps.get_model('users', 'Staff') # Corrected: Assuming Staff is in users app
    User = apps.get_model('auth', 'User') # For deleted_by

    print("Migrating Order data...")
    for old_order in OldOrder.objects.all():
        customer_instance = None
        if old_order.customer_id:
            try:
                customer_instance = NewCustomer.objects.get(id=old_order.customer_id)
            except NewCustomer.DoesNotExist:
                print(f"Warning: Customer with id {old_order.customer_id} for old order {old_order.id} not found. Setting customer to None.")

        order_status_instance = None
        if old_order.order_status_id:
            try:
                order_status_instance = NewOrderStatus.objects.get(id=old_order.order_status_id)
            except NewOrderStatus.DoesNotExist:
                print(f"Warning: OrderStatus with id {old_order.order_status_id} for old order {old_order.id} not found. Setting order_status to None.")

        table_instance = None
        if old_order.table_id:
            try:
                table_instance = NewTable.objects.get(id=old_order.table_id)
            except NewTable.DoesNotExist:
                print(f"Warning: Table with id {old_order.table_id} for old order {old_order.id} not found. Setting table to None.")

        deleted_by_user = None
        if old_order.deleted_by_id:
            try:
                deleted_by_user = User.objects.get(id=old_order.deleted_by_id)
            except User.DoesNotExist:
                print(f"Warning: DeletedBy User with id {old_order.deleted_by_id} for old order {old_order.id} not found. Setting deleted_by to None.")

        waiter_instance = None
        if old_order.waiter_id:
            try:
                waiter_instance = NewStaff.objects.get(id=old_order.waiter_id)
            except NewStaff.DoesNotExist:
                print(f"Warning: Waiter (Staff) with id {old_order.waiter_id} for old order {old_order.id} not found. Setting waiter to None.")

        NewOrder.objects.create(
            id=old_order.id,
            customer=customer_instance,
            ordered_at=old_order.ordered_at,
            printed_at=getattr(old_order, 'printed_at', None),
            deleted_at=getattr(old_order, 'deleted_at', None),
            order_status=order_status_instance,
            total_amount=old_order.total_amount,
            served_at=getattr(old_order, 'served_at', None),
            delivery_address=getattr(old_order, 'delivery_address', ''),
            delivered_at=getattr(old_order, 'delivered_at', None),
            special_instructions=getattr(old_order, 'special_instructions', ''),
            inHold=getattr(old_order, 'inHold', False),
            table=table_instance,
            table_number=getattr(old_order, 'table_number', 'Take Away'),
            deleted_by=deleted_by_user,
            deleted_reason=getattr(old_order, 'deleted_reason', ''),
            waiter=waiter_instance,
            display_id=getattr(old_order, 'display_id', ''),
            previous_table=getattr(old_order, 'previous_table', ''),
        )
    print("Finished migrating Order data.")

def migrate_orders_orderitem_data(apps, schema_editor):
    OldOrderItem = apps.get_model('item', 'OrderItem')
    NewOrderItem = apps.get_model('orders', 'OrderItem')
    NewOrder = apps.get_model('orders', 'Order')
    NewItem = apps.get_model('menu', 'Item')
    NewInvoice = apps.get_model('payments', 'Invoice') # Assuming Invoice is in payments app

    print("Migrating OrderItem data...")
    for old_order_item in OldOrderItem.objects.all():
        order_instance = None
        if old_order_item.order_id:
            try:
                order_instance = NewOrder.objects.get(id=old_order_item.order_id)
            except NewOrder.DoesNotExist:
                print(f"Warning: Order with id {old_order_item.order_id} for old order item {old_order_item.id} not found. Setting order to None.")

        item_instance = None
        if old_order_item.item_id:
            try:
                item_instance = NewItem.objects.get(id=old_order_item.item_id)
            except NewItem.DoesNotExist:
                print(f"Warning: Item with id {old_order_item.item_id} for old order item {old_order_item.id} not found. Setting item to None.")

        invoice_instance = None
        if old_order_item.invoice_id:
            try:
                invoice_instance = NewInvoice.objects.get(id=old_order_item.invoice_id)
            except NewInvoice.DoesNotExist:
                print(f"Warning: Invoice with id {old_order_item.invoice_id} for old order item {old_order_item.id} not found. Setting invoice to None.")

        new_order_item = NewOrderItem.objects.create(
            id=old_order_item.id,
            order=order_instance,
            item=item_instance,
            # Old OrderItem had `quantity` and `price`. `quantity` seems to be missing in your new schema
            # If `quantity` is now handled by `OrderItemExtra` or if you intended to keep it, adjust.
            # Assuming `price` in new `OrderItem` is `price_at_time_of_order` or similar, adjust if field name differs.
            price=old_order_item.price, # This looks like `price` from old model maps to `price` in new
            item_name=getattr(old_order_item, 'item_name', ''),
            item_price=getattr(old_order_item, 'item_price', Decimal('0.00')),
            customizations=getattr(old_order_item, 'customizations', ''),
            invoice=invoice_instance,
            inHold=getattr(old_order_item, 'inHold', False),
        )
        # Migrate ManyToMany 'selected_extras'
        for old_extra in old_order_item.selected_extras.all():
            try:
                new_extra_instance = NewExtra.objects.get(id=old_extra.id)
                new_order_item.selected_extras.add(new_extra_instance)
            except NewExtra.DoesNotExist:
                print(f"Warning: Extra with id {old_extra.id} not found for new order item {new_order_item.id}'s selected_extras.")
    print("Finished migrating OrderItem data.")


def migrate_orders_orderitemextra_data(apps, schema_editor):
    OldOrderItemExtra = apps.get_model('item', 'OrderItemExtra')
    NewOrderItemExtra = apps.get_model('orders', 'OrderItemExtra')
    NewOrderItem = apps.get_model('orders', 'OrderItem')
    NewExtra = apps.get_model('menu', 'Extra')

    print("Migrating OrderItemExtra data...")
    for old_oie in OldOrderItemExtra.objects.all():
        order_item_instance = None
        if old_oie.order_item_id:
            try:
                order_item_instance = NewOrderItem.objects.get(id=old_oie.order_item_id)
            except NewOrderItem.DoesNotExist:
                print(f"Warning: OrderItem with id {old_oie.order_item_id} for old order item extra {old_oie.id} not found. Setting order_item to None.")

        extra_instance = None
        if old_oie.extra_id:
            try:
                extra_instance = NewExtra.objects.get(id=old_oie.extra_id)
            except NewExtra.DoesNotExist:
                print(f"Warning: Extra with id {old_oie.extra_id} for old order item extra {old_oie.id} not found. Setting extra to None.")

        NewOrderItemExtra.objects.create(
            id=old_oie.id,
            order_item=order_item_instance,
            extra=extra_instance,
            quantity=old_oie.quantity,
            extra_name=getattr(old_oie, 'extra_name', ''),
            extra_price=getattr(old_oie, 'extra_price', Decimal('0.00')),
        )
    print("Finished migrating OrderItemExtra data.")

def migrate_orders_discount_data(apps, schema_editor):
    OldDiscount = apps.get_model('item', 'Discount')
    NewDiscount = apps.get_model('orders', 'Discount')
    NewOrder = apps.get_model('orders', 'Order')

    print("Migrating Discount data...")
    for old_discount in OldDiscount.objects.all():
        order_instance = None
        if old_discount.order_id:
            try:
                order_instance = NewOrder.objects.get(id=old_discount.order_id)
            except NewOrder.DoesNotExist:
                print(f"Warning: Order with id {old_discount.order_id} for old discount {old_discount.id} not found. Setting order to None.")

        NewDiscount.objects.create(
            id=old_discount.id,
            order=order_instance,
            discount_code=old_discount.discount_code,
            discount_amount=old_discount.discount_amount,
            inHold=getattr(old_discount, 'inHold', False),
        )
    print("Finished migrating Discount data.")

# --- Migration Functions for Payments App Models ---
def migrate_payments_invoice_data(apps, schema_editor):
    OldInvoice = apps.get_model('item', 'Invoice') # Assuming Invoice was in item app
    NewInvoice = apps.get_model('payments', 'Invoice')
    NewTable = apps.get_model('reservations', 'Table') # Assuming Table is in reservations app
    User = apps.get_model('auth', 'User')

    print("Migrating Invoice data...")
    for old_invoice in OldInvoice.objects.all():
        table_instance = None
        if old_invoice.table_id:
            try:
                table_instance = NewTable.objects.get(id=old_invoice.table_id)
            except NewTable.DoesNotExist:
                print(f"Warning: Table with id {old_invoice.table_id} for old invoice {old_invoice.id} not found. Setting table to None.")

        created_by_user = None
        if old_invoice.created_by_id:
            try:
                created_by_user = User.objects.get(id=old_invoice.created_by_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_invoice.created_by_id} for old invoice {old_invoice.id} not found. Setting created_by to None.")

        NewInvoice.objects.create(
            id=old_invoice.id,
            table=table_instance,
            total_amount=old_invoice.total_amount,
            created_at=old_invoice.created_at,
            updated_at=old_invoice.updated_at,
            created_by=created_by_user,
            is_paid=old_invoice.is_paid,
            status=old_invoice.status,
            inHold=getattr(old_invoice, 'inHold', False),
            display_id=getattr(old_invoice, 'display_id', ''),
        )
    print("Finished migrating Invoice data.")

def migrate_payments_payment_data(apps, schema_editor):
    OldPayment = apps.get_model('item', 'Payment')
    NewPayment = apps.get_model('payments', 'Payment')
    NewInvoice = apps.get_model('payments', 'Invoice')
    User = apps.get_model('auth', 'User')

    print("Migrating Payment data...")
    for old_payment in OldPayment.objects.all():
        invoice_instance = None
        if old_payment.invoice_id:
            try:
                invoice_instance = NewInvoice.objects.get(id=old_payment.invoice_id)
            except NewInvoice.DoesNotExist:
                print(f"Warning: Invoice with id {old_payment.invoice_id} for old payment {old_payment.id} not found. Setting invoice to None.")

        processed_by_user = None
        if old_payment.processed_by_id:
            try:
                processed_by_user = User.objects.get(id=old_payment.processed_by_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_payment.processed_by_id} for old payment {old_payment.id} not found. Setting processed_by to None.")

        NewPayment.objects.create(
            id=old_payment.id,
            invoice=invoice_instance,
            amount=old_payment.amount,
            method=old_payment.method,
            transaction_id=getattr(old_payment, 'transaction_id', ''),
            notes=getattr(old_payment, 'notes', ''),
            created_at=old_payment.created_at,
            processed_by=processed_by_user,
            inHold=getattr(old_payment, 'inHold', False),
        )
    print("Finished migrating Payment data.")

def migrate_payments_unpaidreasonlog_data(apps, schema_editor):
    OldUnpaidReasonLog = apps.get_model('item', 'UnpaidReasonLog')
    NewUnpaidReasonLog = apps.get_model('payments', 'UnpaidReasonLog')
    NewInvoice = apps.get_model('payments', 'Invoice')
    User = apps.get_model('auth', 'User')

    print("Migrating UnpaidReasonLog data...")
    for old_log in OldUnpaidReasonLog.objects.all():
        invoice_instance = None
        if old_log.invoice_id:
            try:
                invoice_instance = NewInvoice.objects.get(id=old_log.invoice_id)
            except NewInvoice.DoesNotExist:
                print(f"Warning: Invoice with id {old_log.invoice_id} for old unpaid reason log {old_log.id} not found. Setting invoice to None.")

        user_instance = None
        if old_log.user_id:
            try:
                user_instance = User.objects.get(id=old_log.user_id)
            except User.DoesNotExist:
                print(f"Warning: User with id {old_log.user_id} for old unpaid reason log {old_log.id} not found. Setting user to None.")

        NewUnpaidReasonLog.objects.create(
            id=old_log.id,
            invoice=invoice_instance,
            user=user_instance,
            reason=old_log.reason,
            created_at=old_log.created_at,
        )
    print("Finished migrating UnpaidReasonLog data.")

# --- Migration Functions for Supplier App Models ---
def migrate_supplier_supplier_data(apps, schema_editor):
    # This function is kept for completeness in case a supplier app is added later.
    # It is not called in the operations list for now.
    OldSupplier = apps.get_model('item', 'Supplier')
    # If NewSupplier doesn't exist, this line will raise an error.
    # It's better to keep this function here and uncomment if a 'supplier' app is created.
    # NewSupplier = apps.get_model('supplier', 'Supplier') # Commented out as app might not exist

    print("Migrating Supplier data (skipped as 'supplier' app does not exist)...")
    # for old_supplier in OldSupplier.objects.all():
    #     NewSupplier.objects.create(
    #         id=old_supplier.id,
    #         name=old_supplier.name,
    #         contact_person=old_supplier.contact_person,
    #         phone_number=old_supplier.phone_number,
    #         address=old_supplier.address,
    #         inHold=getattr(old_supplier, 'inHold', False),
    #     )
    # print("Finished migrating Supplier data.")


class Migration(migrations.Migration):

    dependencies = [
        # This is where you list your dependencies.
        # Include the last migration of the 'item' app (if it exists and contains the old models)
        ('item', '0049_alter_staff_role'), # Corrected dependency based on user's full screenshot
        ('menu', '0001_initial'),
        ('orders', '0001_initial'),
        ('payments', '0001_initial'),
        ('reservations', '0001_initial'),
        ('users', '0001_initial'),
        # Removed ('supplier', '0001_initial') as the 'supplier' app does not exist
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Order of operations is crucial due to foreign key dependencies
        # Migrate base entities first: Categories, Extras, Users
        migrations.RunPython(migrate_menu_category_data),
        migrations.RunPython(migrate_menu_extra_data),
        migrations.RunPython(migrate_staff_staff_data), # Staff depends on auth.User
        migrations.RunPython(migrate_users_customer_data), # Customer depends on auth.User
        # Removed migrate_supplier_supplier_data as the 'supplier' app does not exist
        migrations.RunPython(migrate_reservations_table_data), # Tables are independent

        # Then models that depend on the above (e.g., Items depend on Categories)
        migrations.RunPython(migrate_menu_item_data),
        migrations.RunPython(migrate_menu_item_extras_data), # M2M for Item and Extra

        migrations.RunPython(migrate_orders_orderstatus_data), # OrderStatus is relatively independent
        migrations.RunPython(migrate_orders_dailyordercounter_data), # Independent

        # Then models that depend on Customers, Tables, OrderStatus, Staff, Items
        migrations.RunPython(migrate_reservations_reservation_data), # Depends on Customer, (Table)
        migrations.RunPython(migrate_orders_order_data), # Depends on Customer, OrderStatus, Table, Staff, User

        # Then models that depend on Orders, Items, Invoice
        migrations.RunPython(migrate_payments_invoice_data), # Depends on Table, User
        migrations.RunPython(migrate_orders_orderitem_data), # Depends on Order, Item, Invoice (need to run Invoice migration before this)
        migrations.RunPython(migrate_orders_orderitemextra_data), # Depends on OrderItem, Extra

        # Then models that depend on Payments, Invoices, Orders
        migrations.RunPython(migrate_payments_payment_data), # Depends on Invoice, User
        migrations.RunPython(migrate_payments_unpaidreasonlog_data), # Depends on Invoice, User
        migrations.RunPython(migrate_orders_discount_data), # Depends on Order
        # Removed migrate_orders_deliverydetail_data as the 'DeliveryDetail' model does not exist in 'orders' app
    ]

