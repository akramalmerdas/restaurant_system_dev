# Design Document: Inventory Management System

## Overview

The Inventory Management System is a Django-based application module that tracks raw materials, manages stock levels, automatically deducts inventory when orders are completed, and provides alerts for low or out-of-stock items. The system integrates with the existing restaurant management application's menu and order modules to maintain accurate inventory counts and support data-driven purchasing decisions.

### Key Features
- Raw material tracking with multiple units of measurement
- Purchase transaction recording with supplier information
- Recipe definitions linking menu items to raw materials
- Automatic inventory deduction when orders complete
- Real-time stock level monitoring
- Low-stock and out-of-stock alerts
- Manual inventory adjustments for waste/spoilage
- Comprehensive reporting (consumption, purchases, inventory value)

### Technology Stack
- **Backend Framework**: Django 5.0.7
- **Database**: SQLite (development), PostgreSQL-compatible models
- **Frontend**: HTML, CSS (Bootstrap 5), Vanilla JavaScript
- **Real-time Updates**: Django Channels with Redis (already configured)
- **Testing**: Django TestCase, Hypothesis for property-based testing

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │   Reports    │  │   Alerts     │      │
│  │    Views     │  │    Views     │  │    Views     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Inventory   │  │   Recipe     │  │  Transaction │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Alert      │  │   Report     │                         │
│  │   Service    │  │   Service    │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  RawMaterial │  │    Recipe    │  │  Purchase    │      │
│  │    Model     │  │    Model     │  │ Transaction  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Consumption  │  │   Manual     │  │  Supplier    │      │
│  │ Transaction  │  │ Adjustment   │  │    Model     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Order System Integration**
   - Hook into Order model's status change (when order becomes 'completed')
   - Trigger automatic inventory deduction via Django signals
   - Use existing OrderItem and Order models

2. **Menu System Integration**
   - Link recipes to existing menu.Item model
   - Display inventory availability on menu items
   - Prevent ordering when ingredients are unavailable (optional feature)

3. **User System Integration**
   - Use existing authentication and authorization
   - Leverage staff_member_required decorator for access control
   - Track which staff member performed manual adjustments

## Components and Interfaces

### Models

#### RawMaterial
Represents a basic ingredient or supply item.

```python
class RawMaterial(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('pcs', 'Pieces'),
        ('oz', 'Ounces'),
        ('lb', 'Pounds'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    last_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inHold = models.BooleanField(default=False)
```

#### Recipe
Links menu items to required raw materials.

```python
class Recipe(models.Model):
    menu_item = models.OneToOneField('menu.Item', on_delete=models.CASCADE, related_name='recipe')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inHold = models.BooleanField(default=False)
```

#### RecipeIngredient
Defines quantities of raw materials needed for a recipe.

```python
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        unique_together = ('recipe', 'raw_material')
```

#### PurchaseTransaction
Records inventory purchases from suppliers.

```python
class PurchaseTransaction(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey('inventory.Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### ConsumptionTransaction
Records inventory usage when orders are completed.

```python
class ConsumptionTransaction(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='consumptions')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='inventory_consumptions')
    consumed_at = models.DateTimeField(auto_now_add=True)
```

#### ManualAdjustment
Records manual inventory corrections.

```python
class ManualAdjustment(models.Model):
    REASON_CHOICES = [
        ('waste', 'Waste'),
        ('spoilage', 'Spoilage'),
        ('theft', 'Theft'),
        ('counting_error', 'Counting Error'),
        ('other', 'Other'),
    ]
    
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='adjustments')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)  # Can be positive or negative
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    notes = models.TextField(blank=True, null=True)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    adjusted_at = models.DateTimeField(auto_now_add=True)
```

### Services

#### InventoryService
Core business logic for inventory operations.

**Methods:**
- `get_stock_level(raw_material_id)` - Returns current stock for a material
- `check_stock_status(raw_material_id)` - Returns status: 'adequate', 'low', or 'out'
- `get_low_stock_materials()` - Returns queryset of materials at or below reorder level
- `get_out_of_stock_materials()` - Returns queryset of materials with zero or negative stock
- `update_last_purchase_price(raw_material_id, price)` - Updates the last purchase price

#### TransactionService
Handles all inventory transactions.

**Methods:**
- `record_purchase(raw_material_id, quantity, unit_price, supplier_id, user, notes)` - Records purchase and updates stock
- `record_consumption(order_id)` - Deducts inventory based on order's recipes
- `record_manual_adjustment(raw_material_id, quantity, reason, notes, user)` - Records adjustment and updates stock
- `calculate_consumption_for_order(order_id)` - Returns dict of {raw_material_id: quantity} needed

#### RecipeService
Manages recipe definitions.

**Methods:**
- `create_recipe(menu_item_id, ingredients_list)` - Creates recipe with ingredients
- `update_recipe(recipe_id, ingredients_list)` - Updates recipe ingredients
- `get_recipe_for_item(menu_item_id)` - Returns recipe with ingredients
- `validate_recipe_ingredients(ingredients_list)` - Validates ingredient data structure

#### ReportService
Generates inventory reports.

**Methods:**
- `generate_inventory_value_report()` - Calculates total inventory value
- `generate_consumption_report(start_date, end_date, raw_material_id=None)` - Consumption analysis
- `generate_purchase_report(start_date, end_date, raw_material_id=None)` - Purchase analysis
- `export_report_to_csv(report_data, filename)` - Exports report data

### Views

#### Dashboard Views
- `InventoryDashboardView` (ListView) - Displays all raw materials with stock levels
- `RawMaterialCreateView` (CreateView) - Form to add new raw material
- `RawMaterialUpdateView` (UpdateView) - Form to edit raw material
- `RawMaterialDeleteView` (soft delete) - Marks material as inHold

#### Transaction Views
- `PurchaseTransactionCreateView` (CreateView) - Record new purchase
- `PurchaseTransactionListView` (ListView) - View purchase history
- `ManualAdjustmentCreateView` (CreateView) - Record manual adjustment
- `ManualAdjustmentListView` (ListView) - View adjustment history

#### Recipe Views
- `RecipeCreateView` (CreateView) - Create recipe for menu item
- `RecipeUpdateView` (UpdateView) - Edit recipe ingredients
- `RecipeDetailView` (DetailView) - View recipe details

#### Alert Views
- `LowStockAlertView` (TemplateView) - Display low and out-of-stock materials

#### Report Views
- `InventoryReportView` (TemplateView) - Generate and display reports
- `ConsumptionReportView` (TemplateView) - Consumption analysis
- `PurchaseReportView` (TemplateView) - Purchase analysis

### URL Structure

```
/inventory/
    dashboard/                          # Main inventory dashboard
    raw-materials/
        create/                         # Add new raw material
        <int:pk>/update/                # Edit raw material
        <int:pk>/delete/                # Delete raw material
    purchases/
        create/                         # Record purchase
        list/                           # Purchase history
    adjustments/
        create/                         # Manual adjustment
        list/                           # Adjustment history
    recipes/
        create/<int:menu_item_id>/      # Create recipe for menu item
        <int:pk>/update/                # Edit recipe
        <int:pk>/detail/                # View recipe
    alerts/                             # Low/out-of-stock alerts
    reports/
        inventory-value/                # Inventory value report
        consumption/                    # Consumption report
        purchases/                      # Purchase report
```

## Data Models

### Entity Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐
│   RawMaterial   │◄────────│PurchaseTransaction│
│                 │         │                 │
│ - name          │         │ - quantity      │
│ - unit          │         │ - unit_price    │
│ - current_stock │         │ - total_cost    │
│ - reorder_level │         │ - purchase_date │
└────────┬────────┘         └─────────────────┘
         │                           │
         │                           │
         │                  ┌────────▼────────┐
         │                  │    Supplier     │
         │                  │                 │
         │                  │ - name          │
         │                  │ - contact_person│
         │                  └─────────────────┘
         │
         │
    ┌────▼────────────┐
    │RecipeIngredient │
    │                 │
    │ - quantity      │
    └────┬────────────┘
         │
         │
    ┌────▼────────┐         ┌─────────────────┐
    │   Recipe    │         │   menu.Item     │
    │             │◄────────│                 │
    └─────────────┘         │ - name          │
                            │ - price         │
                            └────────┬────────┘
                                     │
                                     │
                            ┌────────▼────────┐
                            │  orders.Order   │
                            │                 │
                            │ - order_status  │
                            └────────┬────────┘
                                     │
                                     │
┌─────────────────┐         ┌────────▼────────────┐
│   RawMaterial   │◄────────│ConsumptionTransaction│
│                 │         │                     │
└─────────────────┘         │ - quantity          │
         ▲                  │ - consumed_at       │
         │                  └─────────────────────┘
         │
         │
┌────────┴────────┐
│ManualAdjustment │
│                 │
│ - quantity      │
│ - reason        │
│ - notes         │
└─────────────────┘
```

### Data Flow

1. **Purchase Flow**
   ```
   User → PurchaseTransactionCreateView → TransactionService.record_purchase()
   → Update RawMaterial.current_stock → Update RawMaterial.last_purchase_price
   ```

2. **Order Completion Flow**
   ```
   Order.status = 'completed' → post_save signal → TransactionService.record_consumption()
   → RecipeService.get_recipe_for_item() → Calculate total quantities
   → Create ConsumptionTransaction records → Update RawMaterial.current_stock
   ```

3. **Manual Adjustment Flow**
   ```
   User → ManualAdjustmentCreateView → TransactionService.record_manual_adjustment()
   → Create ManualAdjustment record → Update RawMaterial.current_stock
   ```

## Error Handling

### Validation Errors
- **Empty Material Name**: Display form error "Material name is required"
- **Negative Purchase Quantity**: Display form error "Quantity must be positive"
- **Missing Recipe Quantity**: Display form error "Ingredient quantity is required"
- **Missing Adjustment Reason**: Display form error "Reason for adjustment is required"

### Business Logic Errors
- **Insufficient Stock**: Allow negative stock but flag material as out-of-stock
- **Missing Recipe**: Log warning, skip consumption for that menu item
- **Invalid Unit Conversion**: Display error "Unit mismatch for ingredient"

### System Errors
- **Database Connection**: Display user-friendly error page
- **Signal Processing Failure**: Log error, send admin notification, continue order processing
- **Report Generation Failure**: Display error message, log details

### Error Logging
- Use Django's logging framework
- Log all transaction failures at ERROR level
- Log validation failures at WARNING level
- Log successful operations at INFO level

## Testing Strategy

### Unit Testing
Unit tests will verify specific examples and edge cases:

1. **Model Tests**
   - Test RawMaterial creation with valid data
   - Test Recipe creation and ingredient association
   - Test transaction model creation
   - Test soft delete functionality (inHold flag)

2. **Service Tests**
   - Test InventoryService.get_stock_level() with known material
   - Test TransactionService.record_purchase() updates stock correctly
   - Test RecipeService.create_recipe() with valid ingredients
   - Test ReportService calculations with sample data

3. **View Tests**
   - Test dashboard displays materials correctly
   - Test purchase form submission
   - Test recipe creation form
   - Test access control (staff_member_required)

4. **Integration Tests**
   - Test complete purchase workflow
   - Test order completion triggers consumption
   - Test manual adjustment workflow

### Property-Based Testing

Property-based tests will use **Hypothesis** library to verify universal properties across all inputs. Each test will run a minimum of 100 iterations.

#### Testing Framework Configuration
```python
from hypothesis import given, settings
from hypothesis.extra.django import from_model
from hypothesis import strategies as st

# Configure Hypothesis for Django
settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Raw material creation persistence
*For any* valid raw material with name, unit, and stock quantity, creating the material then retrieving it should return the same values for all fields.
**Validates: Requirements 1.1**

### Property 2: Valid unit acceptance
*For any* raw material created with a unit from the valid set (kg, g, l, ml, pcs, oz, lb), the creation should succeed and the unit should be stored correctly.
**Validates: Requirements 1.2**

### Property 3: Material display completeness
*For any* raw material, the rendered display should contain the material name, unit, current stock, and reorder level.
**Validates: Requirements 1.3**

### Property 4: Material update persistence
*For any* raw material and any valid update to its fields, saving the update then retrieving the material should show the updated values.
**Validates: Requirements 1.4**

### Property 5: Purchase transaction persistence
*For any* valid purchase transaction data (material, quantity, unit price, supplier, date), creating the transaction should persist all fields correctly.
**Validates: Requirements 2.1**

### Property 6: Purchase increases stock
*For any* raw material and any positive purchase quantity, the stock level after recording the purchase should equal the stock level before plus the purchased quantity.
**Validates: Requirements 2.2**

### Property 7: Purchase history ordering
*For any* set of purchase transactions, when displayed in purchase history, they should be ordered by purchase date in descending order.
**Validates: Requirements 2.3**

### Property 8: Multi-material purchase atomicity
*For any* purchase transaction involving multiple raw materials, all material stock levels should be updated correctly by their respective quantities.
**Validates: Requirements 2.4**

### Property 9: Recipe creation persistence
*For any* menu item and any valid list of ingredients (material + quantity pairs), creating a recipe should persist the menu item reference and all ingredients correctly.
**Validates: Requirements 3.1**

### Property 10: Recipe ingredient validation
*For any* recipe ingredient, the quantity should be positive and the unit should match the raw material's unit.
**Validates: Requirements 3.2**

### Property 11: Recipe display completeness
*For any* recipe, the rendered display should contain the menu item name and all ingredients with their quantities and units.
**Validates: Requirements 3.3**

### Property 12: Recipe update persistence
*For any* recipe and any valid update to its ingredients, saving the update then retrieving the recipe should show the updated ingredients, and subsequent order processing should use the new recipe.
**Validates: Requirements 3.4**

### Property 13: Order completion identifies all items
*For any* order with any set of menu items, when the order status changes to completed, the system should correctly identify all menu items in the order.
**Validates: Requirements 4.1**

### Property 14: Recipe retrieval for order items
*For any* set of menu items that have recipes, the system should retrieve all recipes correctly.
**Validates: Requirements 4.2**

### Property 15: Consumption quantity aggregation
*For any* order containing multiple items with recipes, the total quantity of each raw material needed should equal the sum of that material's quantities across all recipes (accounting for item quantities).
**Validates: Requirements 4.3**

### Property 16: Consumption decreases stock
*For any* raw material and any consumption quantity, the stock level after recording consumption should equal the stock level before minus the consumed quantity.
**Validates: Requirements 4.4**

### Property 17: Insufficient stock handling
*For any* order where a raw material has insufficient stock, the consumption transaction should still be recorded, the stock should go negative, and the material should be flagged as out of stock.
**Validates: Requirements 4.5**

### Property 18: Dashboard displays all materials
*For any* set of raw materials (not marked inHold), the inventory dashboard should display all of them with their current stock quantities and units.
**Validates: Requirements 5.1**

### Property 19: Dashboard alphabetical sorting
*For any* set of raw materials displayed on the dashboard, they should be sorted alphabetically by name.
**Validates: Requirements 5.2**

### Property 20: Low stock warning indicator
*For any* raw material where current stock is at or below the reorder level (and above zero), the dashboard display should include a warning indicator.
**Validates: Requirements 5.3**

### Property 21: Out of stock critical indicator
*For any* raw material where current stock is zero or negative, the dashboard display should include a critical alert indicator.
**Validates: Requirements 5.4**

### Property 22: Dashboard timestamp display
*For any* raw material displayed on the dashboard, the display should include the last updated timestamp.
**Validates: Requirements 5.5**

### Property 23: Reorder level persistence
*For any* raw material and any valid reorder level value, setting the reorder level then retrieving the material should show the same reorder level.
**Validates: Requirements 6.1**

### Property 24: Reorder status evaluation
*For any* raw material where stock level falls to or below the reorder level, the material should be marked as requiring reorder.
**Validates: Requirements 6.2**

### Property 25: Low stock report filtering
*For any* set of raw materials, the low-stock report should include exactly those materials where current stock is at or below the reorder level and the reorder level is not null.
**Validates: Requirements 6.3**

### Property 26: Null reorder level exclusion
*For any* raw material with a null reorder level, it should not appear in low-stock alerts regardless of stock level.
**Validates: Requirements 6.4**

### Property 27: Reorder level update immediacy
*For any* raw material, when the reorder level is updated, the material's presence in low-stock alerts should immediately reflect the new reorder level.
**Validates: Requirements 6.5**

### Property 28: Alert page partitioning
*For any* set of raw materials, the alerts page should correctly partition them into two lists: low-stock (0 < stock <= reorder_level) and out-of-stock (stock <= 0).
**Validates: Requirements 7.1**

### Property 29: Low stock list filtering
*For any* set of raw materials, the low-stock list should include exactly those where 0 < current stock <= reorder level.
**Validates: Requirements 7.2**

### Property 30: Out of stock list filtering
*For any* set of raw materials, the out-of-stock list should include exactly those where current stock <= 0.
**Validates: Requirements 7.3**

### Property 31: Alert list display completeness
*For any* material in an alert list, the display should include material name, current stock, reorder level, and unit.
**Validates: Requirements 7.4**

### Property 32: Consumption report ordering
*For any* set of consumption transactions, when displayed in the consumption report, they should be ordered by consumed_at timestamp in descending order.
**Validates: Requirements 8.1**

### Property 33: Consumption transaction display completeness
*For any* consumption transaction, the display should include raw material name, quantity consumed, order reference, and timestamp.
**Validates: Requirements 8.2**

### Property 34: Consumption date range filtering
*For any* date range filter, the consumption report should include exactly those transactions where consumed_at falls within the specified range.
**Validates: Requirements 8.3**

### Property 35: Consumption material filtering
*For any* raw material filter, the consumption report should include exactly those transactions for the selected material.
**Validates: Requirements 8.4**

### Property 36: Consumption total aggregation
*For any* set of consumption transactions (possibly filtered), the displayed total quantity for each material should equal the sum of all consumption quantities for that material.
**Validates: Requirements 8.5**

### Property 37: Manual adjustment persistence
*For any* valid manual adjustment data (material, quantity, reason, notes), creating the adjustment should persist all fields correctly.
**Validates: Requirements 9.1**

### Property 38: Adjustment updates stock
*For any* raw material and any adjustment quantity (positive or negative), the stock level after recording the adjustment should equal the stock level before plus the adjustment quantity.
**Validates: Requirements 9.2**

### Property 39: Adjustment history display completeness
*For any* manual adjustment, the display should include material name, quantity, reason, and adjusted_at timestamp.
**Validates: Requirements 9.3**

### Property 40: Adjustment transaction type distinction
*For any* manual adjustment, it should be stored as a distinct transaction type and not be confused with purchase or consumption transactions.
**Validates: Requirements 9.5**

### Property 41: Inventory value calculation
*For any* set of raw materials with stock quantities and last purchase prices, the total inventory value should equal the sum of (stock quantity × last purchase price) for each material with a non-null price.
**Validates: Requirements 10.1**

### Property 42: Consumption report aggregation
*For any* date range, the consumption report should show total quantities consumed for each raw material equal to the sum of all consumption quantities in that range.
**Validates: Requirements 10.2**

### Property 43: Purchase report aggregation
*For any* date range, the purchase report should show total quantities purchased and total costs for each raw material equal to the sum of all purchase quantities and costs in that range.
**Validates: Requirements 10.3**

### Property 44: Null price exclusion from value
*For any* raw material with a null last_purchase_price, it should be excluded from inventory value calculations.
**Validates: Requirements 10.5**

## Testing Strategy (Continued)

### Property-Based Test Implementation

Each correctness property will be implemented as a property-based test using Hypothesis. Tests will be tagged with comments referencing the property number and requirement.

**Example Property Test Structure:**
```python
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.django import from_model
from decimal import Decimal

class TestInventoryProperties(TestCase):
    
    @given(
        name=st.text(min_size=1, max_size=255),
        unit=st.sampled_from(['kg', 'g', 'l', 'ml', 'pcs', 'oz', 'lb']),
        stock=st.decimals(min_value=0, max_value=9999, places=3)
    )
    @settings(max_examples=100)
    def test_property_1_raw_material_creation_persistence(self, name, unit, stock):
        """
        Feature: inventory-management, Property 1: Raw material creation persistence
        Validates: Requirements 1.1
        """
        # Create material
        material = RawMaterial.objects.create(
            name=name,
            unit=unit,
            current_stock=stock
        )
        
        # Retrieve material
        retrieved = RawMaterial.objects.get(id=material.id)
        
        # Verify all fields match
        self.assertEqual(retrieved.name, name)
        self.assertEqual(retrieved.unit, unit)
        self.assertEqual(retrieved.current_stock, stock)
```

### Test Coverage Goals
- **Unit Tests**: 80% code coverage minimum
- **Property Tests**: All 44 correctness properties implemented
- **Integration Tests**: All major workflows covered
- **Edge Cases**: All validation scenarios tested

### Continuous Integration
- Run all tests on every commit
- Block merges if tests fail
- Generate coverage reports
- Run property tests with 100 iterations in CI

## Implementation Notes

### Django Signals for Automatic Consumption

Use Django's post_save signal to trigger inventory deduction when orders are completed:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order

@receiver(post_save, sender=Order)
def handle_order_completion(sender, instance, created, **kwargs):
    if not created and instance.order_status.name == 'completed':
        # Check if we've already processed this order
        if not instance.inventory_consumptions.exists():
            TransactionService.record_consumption(instance.id)
```

### Performance Considerations

1. **Database Indexing**
   - Index on RawMaterial.name for search
   - Index on ConsumptionTransaction.consumed_at for date filtering
   - Index on PurchaseTransaction.purchase_date for date filtering
   - Composite index on (raw_material_id, consumed_at) for material-specific reports

2. **Query Optimization**
   - Use select_related() for foreign key lookups
   - Use prefetch_related() for reverse foreign key lookups
   - Implement pagination for large lists
   - Cache dashboard queries for 5 minutes

3. **Transaction Management**
   - Wrap multi-material purchases in database transactions
   - Use atomic blocks for consumption recording
   - Implement retry logic for signal processing failures

### Security Considerations

1. **Access Control**
   - All inventory views require staff authentication
   - Use @staff_member_required decorator
   - Implement role-based permissions (manager vs. staff)

2. **Input Validation**
   - Sanitize all user inputs
   - Validate decimal precision
   - Prevent SQL injection through ORM usage
   - Validate file uploads for reports

3. **Audit Trail**
   - Log all manual adjustments with user information
   - Track who created/modified recipes
   - Maintain transaction history indefinitely

### Migration Strategy

1. **Initial Migration**
   - Create all new models
   - Migrate existing Inventory and Supplier models if needed
   - Create default units of measurement

2. **Data Migration**
   - If existing inventory data exists, create RawMaterial records
   - Set initial stock levels from existing data
   - Create initial recipes for existing menu items (manual process)

3. **Rollback Plan**
   - Keep old inventory system running in parallel for 1 week
   - Verify data accuracy before full cutover
   - Maintain database backups before migration

## Future Enhancements

1. **Predictive Ordering**
   - Analyze consumption patterns
   - Suggest optimal reorder quantities
   - Predict when materials will run out

2. **Supplier Management**
   - Track supplier performance
   - Compare prices across suppliers
   - Automated purchase order generation

3. **Waste Tracking**
   - Detailed waste categorization
   - Waste reduction analytics
   - Cost of waste reporting

4. **Mobile App**
   - Quick stock checks on mobile
   - Barcode scanning for purchases
   - Push notifications for low stock

5. **Integration with POS**
   - Real-time inventory updates
   - Automatic recipe scaling
   - Menu item availability based on stock

## Glossary Reference

All terms used in this design document are defined in the Requirements Document Glossary section. Key terms include:
- Inventory System
- Raw Material
- Stock Level
- Reorder Level
- Recipe
- Purchase Transaction
- Consumption Transaction
- Unit of Measurement
