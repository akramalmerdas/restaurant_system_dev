import { showConfirmation } from "./custom_dialog.js";


document.addEventListener('DOMContentLoaded', () => {
    const invoiceBtn = document.getElementById('generateInvoiceBtn');
    
    invoiceBtn.addEventListener('click', () => {
        // Your generateInvoice functionality here
        console.log('Invoice generation triggered');
        generateInvoice();
    });



    const invoiceBtnByItem = document.getElementById('generateInvoiceBtnByItem');
    
    invoiceBtnByItem.addEventListener('click', () => {
        // Your generateInvoice functionality here
        console.log('Invoice generation triggered');
        generateInvoiceByItem();
    }); 
});

function generateInvoice() {
    // 1. Get the table ID from the data attribute on the .table-info element.
    const tableInfoElement = document.querySelector('.table-info');
    if (!tableInfoElement) {
        alert('Error: Could not find table information on the page.');
        return;
    }
    const tableId = tableInfoElement.dataset.tableId;

    if (!tableId) {
        alert('Error: Table ID is missing.');
        return;
    }

    showConfirmation("Do you want to generate the invoice for all the items in this table?", function(confirmed) {
          if (confirmed) {
       // 2. Call the NEW, secure endpoint.
    fetch('/generate-invoice-by-table/', { // <-- Use the new URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Ensure you have this helper function
        },
        // 3. Send ONLY the table_id. The server will do the rest.
        body: JSON.stringify({
            table_id: tableId
        })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 200 && body.success) {
            alert(body.message || 'Invoice generated successfully!');
            // Redirect to a fresh page after success
            setTimeout(() => {
                window.location.href = document.body.dataset.tableLandingUrl || '/reservations/table_landing/';
            }, 500);
        } else {
            // Display the specific error message from the server
            alert('Error: ' + (body.message || 'An unknown error occurred.'));
        }
    })
    .catch(error => {
        console.error('Invoice Generation Error:', error);
        alert('A network or unexpected error occurred during invoice generation.');
    });         
          } else {
              alert("Action canceled.");
              return;
          }
      });

    
}

function generateInvoiceByItem() {
    // --- 1. CORRECTED: Get table ID ---
    // We select the element that has the 'data-table-id' attribute.
    const tableElement = document.querySelector('[data-table-id]');
    if (!tableElement) {
        // This selector should match the table element on your page.
        // If this fails, check your HTML for an element with data-table-id.
        alert('Critical Error: Table information container not found on the page.');
        return;
    }
    const tableId = tableElement.dataset.tableId;
    if (!tableId) {
        alert('Error: Table ID is missing from the element.');
        return;
    }
    
    // --- 2. Get all checked item checkboxes ---
    // This selector is still correct.
    const checkedCheckboxes = document.querySelectorAll('.item-checkbox:checked');
    if (checkedCheckboxes.length === 0) {
        alert('No items selected. Please select at least one item.');
        return;
    }
    
    // --- 3. CORRECTED: Extract item IDs from the 'value' attribute ---
    // The 'value' attribute is the standard place to store the ID for an input.
    const itemIds = Array.from(checkedCheckboxes).map(checkbox => checkbox.value);

    console.log('Preparing to generate invoice for Table ID:', tableId, 'with Item IDs:', itemIds);

    // --- 4. The rest of your fetch logic is already correct ---
    showConfirmation("Do you want to generate the invoice for all the items in this table?", function(confirmed) {
        if (confirmed) {
            fetch('/generate-invoice-by-item/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    item_ids: itemIds,
                    table_id: tableId
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.message || 'Request failed');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert(`Invoice generated successfully for ${itemIds.length} items!`);
                    setTimeout(() => {
                        window.location.href = document.body.dataset.tableLandingUrl || '/reservations/table_landing/'; // Or wherever you need to redirect
                    }, 500);
                } else {
                    alert('Error: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Invoice generation failed: ' + error.message);
            });
        } else {
            alert("Action canceled.");
            return;
        }
    });
 
}

        function showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '9999';
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }



        function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
        // Add click handlers for status updates
        document.querySelectorAll('.order-status').forEach(status => {
            status.addEventListener('click', function() {
                const currentStatus = this.textContent.trim().toLowerCase();
                let newStatus = '';
                let newClass = '';
                
                switch(currentStatus) {
                    case 'pending':
                        newStatus = 'Preparing';
                        newClass = 'status-preparing';
                        break;
                    case 'preparing':
                        newStatus = 'Ready';
                        newClass = 'status-ready';
                        break;
                    case 'ready':
                        newStatus = 'Served';
                        newClass = 'status-served';
                        break;
                    case 'served':
                        newStatus = 'Printed';
                        newClass = 'status-printed';
                        break;
                    default:
                        return;
                }
                
                this.className = `order-status ${newClass}`;
                this.textContent = newStatus;
                
                showNotification(`Order status updated to ${newStatus}`, 'info');
            });
        });
        
        // Auto-refresh page every 30 seconds to get updated order status
        setInterval(function() {
            if (document.querySelectorAll('.status-pending, .status-preparing').length > 0) {
                location.reload();
            }
        }, 30000);
        
