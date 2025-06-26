document.addEventListener("DOMContentLoaded", () => {
    // JavaScript function to update invoice status
    window.updateInvoiceStatus = function(invoiceId, status) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(`/invoice/${invoiceId}/change-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include CSRF token in the headers
            },
            body: JSON.stringify({ is_paid: status }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update invoice status');
            }
            return response.json();
        })
        .then(data => {
            alert('Status updated successfully:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
});


document.addEventListener("DOMContentLoaded", function() {
  
    let generateInvoiceButton = document.getElementById('generate-invoice-btn');
   
if(generateInvoiceButton){
    

    generateInvoiceButton.addEventListener('click', function(event) {
        event.preventDefault();  // Prevent the default link behavior
    
        
        
        const tableId = generateInvoiceButton.getAttribute('data-table-id');

        const selectedOrders = Array.from(document.querySelectorAll('input[name="order_select"]:checked'))
        .map(input => input.value);  // Get values of checked checkboxes
     
          fetch(`/generate_invoice/${tableId}/`, {
           method: 'POST',
           headers: {
          'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
       },
        body: JSON.stringify({ order_select: selectedOrders })  // Send selected orders as JSON
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Invoice created successfully! Invoice ID: ' + data.invoice_id);
                // Optionally, update the UI to show the invoice details or redirect to the invoice page
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your request.');
        });
    });
    
    } 

});


function printInvoice(invoiceId) {
    // Open the invoice in a new window for printing
    const printWindow = window.open(`/print_invoice/${invoiceId}/`, '_blank');
    
    // This is a fallback in case the popup is blocked
    if (!printWindow || printWindow.closed || typeof printWindow.closed == 'undefined') {
        // If popup is blocked, redirect to the print page in the same window
        window.location.href = `/print_invoice/${invoiceId}/`;
    }
}

// Add click handler for print buttons (in case the inline onclick doesn't work)
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-print').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const invoiceId = this.getAttribute('data-invoice-id') || 
                             this.closest('tr').querySelector('td:first-child').textContent.trim();
            printInvoice(invoiceId);
        });
    });
});