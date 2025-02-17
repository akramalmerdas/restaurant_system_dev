  API Documentation
=================

MochaCafe provides a RESTful API for interacting with the application programmatically.

### Endpoints

- **GET /api/orders/**: Retrieve a list of orders.
- **POST /api/orders/**: Create a new order.
- **GET /api/orders/{id}/**: Retrieve details of a specific order.
- **PUT /api/orders/{id}/**: Update an existing order.
- **DELETE /api/orders/{id}/**: Delete an order.

### Authentication

API requests require authentication via token. Obtain a token by logging in with your credentials.

### Detailed Endpoints

- **GET /meal/{menu_item_id}/**: Retrieve details of a specific menu item.
- **GET /get-extras/{menu_item_id}/**: Retrieve extras for a specific menu item.
- **GET /order_details/**: Retrieve order details.
- **GET /order_view/{order_id}/**: View a specific order.
- **GET /orders/**: List all orders.
- **POST /add_to_order/**: Add an item to an order.
- **POST /order_details/delete_item/{item_id}/**: Delete an item from an order.
- **POST /submit_order/**: Submit an order.
- **POST /print_order/**: Print an order.
- **POST /login/**: User login.
- **GET /admin_dashboard/**: Access the admin dashboard.
- **POST /customer_signup/**: Sign up a new customer.
- **POST /signup/**: User signup.
- **POST /logout/**: User logout.
- **GET /profile/**: Retrieve customer profile.
- **POST /delete_order/{order_id}/**: Delete a specific order.
- **POST /update_order_status/{order_id}/**: Update the status of an order.
- **GET /print_order_view/{order_id}/**: View the print version of an order.
- **GET /generate_invoice/{table_id}/**: Generate an invoice for a table.
- **GET /invoices/**: Access the invoice dashboard.
- **GET /invoice/{invoice_id}/**: View a specific invoice.
- **POST /invoice/{invoice_id}/change-status/**: Change the status of an invoice.
