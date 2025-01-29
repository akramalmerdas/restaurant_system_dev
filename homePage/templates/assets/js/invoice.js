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


generateInvoiceButton=document.getElementById('generate-invoice-btn')


if(generateInvoiceButton){
    

generateInvoiceButton.addEventListener('click', function(event) {
    event.preventDefault();  // Prevent the default link behavior

    const tableId = 1;  // Replace with the actual table ID you want to close (you can dynamically get this from the page)

    fetch(`/generate-invoice/${tableId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ table_id: tableId })
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