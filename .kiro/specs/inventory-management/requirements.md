# Requirements Document

## Introduction

This document specifies the requirements for an Inventory Management System for a restaurant application. The system will track raw materials and ingredients, automatically deduct inventory when meals are sold, monitor stock levels, and provide alerts when items are running low or out of stock. This enables restaurant managers to maintain optimal inventory levels, reduce waste, and prevent stockouts.

## Glossary

- **Inventory System**: The software component responsible for tracking, managing, and reporting on raw materials and ingredients
- **Raw Material**: A basic ingredient or supply item used to prepare menu items (e.g., flour, tomatoes, chicken)
- **Stock Level**: The current quantity of a raw material available in inventory
- **Reorder Level**: The minimum quantity threshold that triggers a low-stock alert
- **Recipe**: A specification that defines which raw materials and quantities are required to prepare a menu item
- **Purchase Transaction**: A record of raw materials acquired from suppliers
- **Consumption Transaction**: A record of raw materials used when preparing menu items
- **Menu Item**: A dish or product available for sale to customers (already defined in the menu.Item model)
- **Order**: A customer's request for one or more menu items (already defined in the orders.Order model)
- **Unit of Measurement**: The standard unit used to quantify a raw material (e.g., kg, liters, pieces)

## Requirements

### Requirement 1

**User Story:** As a restaurant manager, I want to define raw materials with their units of measurement, so that I can track different types of inventory items accurately.

#### Acceptance Criteria

1. WHEN a manager creates a raw material THEN the Inventory System SHALL store the material name, unit of measurement, and current stock quantity
2. WHEN a manager specifies a unit of measurement THEN the Inventory System SHALL support common units including kilograms, grams, liters, milliliters, and pieces
3. WHEN a manager views a raw material THEN the Inventory System SHALL display the material name, unit, current stock, and reorder level
4. WHEN a manager updates raw material information THEN the Inventory System SHALL persist the changes immediately
5. WHEN a manager attempts to create a raw material with an empty name THEN the Inventory System SHALL reject the creation and display a validation error

### Requirement 2

**User Story:** As a restaurant manager, I want to record inventory purchases from suppliers, so that I can track what materials I've acquired and maintain accurate stock levels.

#### Acceptance Criteria

1. WHEN a manager records a purchase transaction THEN the Inventory System SHALL store the raw material, quantity purchased, unit price, supplier, purchase date, and total cost
2. WHEN a purchase transaction is saved THEN the Inventory System SHALL increase the raw material's stock level by the purchased quantity
3. WHEN a manager views purchase history THEN the Inventory System SHALL display all transactions sorted by date in descending order
4. WHEN a purchase transaction includes multiple raw materials THEN the Inventory System SHALL update stock levels for all materials in a single transaction
5. WHEN a manager attempts to record a purchase with zero or negative quantity THEN the Inventory System SHALL reject the transaction and display a validation error

### Requirement 3

**User Story:** As a restaurant manager, I want to define recipes that specify which raw materials are needed for each menu item, so that the system can automatically deduct inventory when meals are sold.

#### Acceptance Criteria

1. WHEN a manager creates a recipe for a menu item THEN the Inventory System SHALL store the menu item reference and a list of required raw materials with quantities
2. WHEN a recipe specifies a raw material quantity THEN the Inventory System SHALL validate that the quantity is positive and uses the correct unit of measurement
3. WHEN a manager views a recipe THEN the Inventory System SHALL display the menu item name and all required raw materials with their quantities and units
4. WHEN a manager updates a recipe THEN the Inventory System SHALL persist the changes and apply them to future order processing
5. WHEN a manager attempts to add a raw material to a recipe without specifying quantity THEN the Inventory System SHALL reject the addition and display a validation error

### Requirement 4

**User Story:** As a restaurant manager, I want the system to automatically deduct raw materials from inventory when orders are completed, so that stock levels remain accurate without manual tracking.

#### Acceptance Criteria

1. WHEN an order status changes to completed THEN the Inventory System SHALL identify all menu items in the order
2. WHEN menu items are identified THEN the Inventory System SHALL retrieve the recipe for each menu item
3. WHEN recipes are retrieved THEN the Inventory System SHALL calculate the total quantity of each raw material needed across all menu items
4. WHEN quantities are calculated THEN the Inventory System SHALL deduct the required amounts from the corresponding raw material stock levels
5. WHEN a raw material has insufficient stock to fulfill an order THEN the Inventory System SHALL record the consumption transaction but allow the stock level to go negative and flag the material as out of stock

### Requirement 5

**User Story:** As a restaurant manager, I want to view current stock levels for all raw materials, so that I can quickly assess what inventory I have available.

#### Acceptance Criteria

1. WHEN a manager accesses the inventory dashboard THEN the Inventory System SHALL display all raw materials with their current stock quantities and units
2. WHEN displaying stock levels THEN the Inventory System SHALL sort materials alphabetically by name
3. WHEN a raw material's stock is at or below its reorder level THEN the Inventory System SHALL highlight the material with a warning indicator
4. WHEN a raw material's stock is zero or negative THEN the Inventory System SHALL highlight the material with a critical alert indicator
5. WHEN the dashboard is displayed THEN the Inventory System SHALL show the last updated timestamp for each material's stock level

### Requirement 6

**User Story:** As a restaurant manager, I want to set reorder levels for raw materials, so that I receive alerts when stock is running low and need to reorder.

#### Acceptance Criteria

1. WHEN a manager sets a reorder level for a raw material THEN the Inventory System SHALL store the threshold quantity
2. WHEN a raw material's stock level falls to or below the reorder level THEN the Inventory System SHALL mark the material as requiring reorder
3. WHEN a manager views the low-stock report THEN the Inventory System SHALL display all materials at or below their reorder levels
4. WHEN a reorder level is not set for a raw material THEN the Inventory System SHALL not generate low-stock alerts for that material
5. WHEN a manager updates a reorder level THEN the Inventory System SHALL immediately re-evaluate the material's stock status

### Requirement 7

**User Story:** As a restaurant manager, I want to view a list of materials that are low in stock or out of stock, so that I can prioritize purchasing decisions.

#### Acceptance Criteria

1. WHEN a manager accesses the alerts page THEN the Inventory System SHALL display two separate lists for low-stock and out-of-stock materials
2. WHEN displaying low-stock materials THEN the Inventory System SHALL show materials where current stock is at or below the reorder level but above zero
3. WHEN displaying out-of-stock materials THEN the Inventory System SHALL show materials where current stock is zero or negative
4. WHEN displaying alert lists THEN the Inventory System SHALL include material name, current stock, reorder level, and unit for each material
5. WHEN no materials meet the alert criteria THEN the Inventory System SHALL display a message indicating all stock levels are adequate

### Requirement 8

**User Story:** As a restaurant manager, I want to view consumption history for raw materials, so that I can analyze usage patterns and optimize purchasing.

#### Acceptance Criteria

1. WHEN a manager accesses consumption reports THEN the Inventory System SHALL display all consumption transactions sorted by date in descending order
2. WHEN displaying a consumption transaction THEN the Inventory System SHALL show the raw material, quantity consumed, associated order reference, and timestamp
3. WHEN a manager filters consumption by date range THEN the Inventory System SHALL display only transactions within the specified period
4. WHEN a manager filters consumption by raw material THEN the Inventory System SHALL display only transactions for the selected material
5. WHEN displaying consumption totals THEN the Inventory System SHALL calculate and show the total quantity consumed for each material in the filtered view

### Requirement 9

**User Story:** As a restaurant manager, I want to manually adjust inventory levels, so that I can correct discrepancies from waste, spoilage, or counting errors.

#### Acceptance Criteria

1. WHEN a manager creates a manual adjustment THEN the Inventory System SHALL store the raw material, adjustment quantity (positive or negative), reason, and timestamp
2. WHEN a manual adjustment is saved THEN the Inventory System SHALL update the raw material's stock level by the adjustment quantity
3. WHEN a manager views adjustment history THEN the Inventory System SHALL display all manual adjustments with material name, quantity, reason, and date
4. WHEN a manager attempts to create an adjustment without a reason THEN the Inventory System SHALL reject the adjustment and display a validation error
5. WHEN an adjustment is recorded THEN the Inventory System SHALL maintain the adjustment as a separate transaction type distinct from purchases and consumption

### Requirement 10

**User Story:** As a restaurant manager, I want to generate inventory reports, so that I can analyze stock value, turnover rates, and purchasing patterns.

#### Acceptance Criteria

1. WHEN a manager generates an inventory value report THEN the Inventory System SHALL calculate the total value by multiplying each material's stock quantity by its most recent purchase unit price
2. WHEN a manager generates a consumption report for a date range THEN the Inventory System SHALL show total quantities consumed for each raw material
3. WHEN a manager generates a purchase report for a date range THEN the Inventory System SHALL show total quantities purchased and total costs for each raw material
4. WHEN displaying reports THEN the Inventory System SHALL provide export functionality to CSV or PDF format
5. WHEN a raw material has no recent purchase price THEN the Inventory System SHALL exclude it from value calculations and note it in the report
