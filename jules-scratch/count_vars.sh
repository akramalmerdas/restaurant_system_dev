#!/bin/bash
FILES=(
    ./homePage/templates/assets/css/meal_page.css
    ./homePage/templates/assets/css/order_page.css
    ./homePage/templates/assets/css/delete_orders.css
    ./homePage/templates/assets/css/style.css
    ./homePage/templates/assets/css/table_dashboard.css
    ./homePage/templates/assets/css/tables_landing.css
    ./homePage/templates/assets/css/admin_dashboard.css
    ./homePage/templates/assets/css/order_view.css
    ./homePage/templates/assets/css/reports.css
    ./homePage/templates/assets/css/waiter_order.css
    ./static/item/css/item_form.css
    ./static/item/css/item_dashboard.css
    ./static/css/edit_branding.css
    ./static/css/meal_page_refactored.css
    ./static/css/invoiceA4.css
    ./static/css/customer_signup.css
    ./static/css/admin_dashboard_refactored.css
    ./static/css/customer_profile.css
)

echo "Primary Color Usage:"
for FILE in "${FILES[@]}"
do
    echo -n "$FILE: "
    grep -o 'var(--primary-color' "$FILE" | wc -l
done

echo ""
echo "Secondary Color Usage:"
for FILE in "${FILES[@]}"
do
    echo -n "$FILE: "
    grep -o 'var(--secondary-color' "$FILE" | wc -l
done
