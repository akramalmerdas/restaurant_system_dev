/**
 * Utility function to get CSRF token from cookies.
 * @returns {string | null} The CSRF token or null if not found.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Displays a toast notification.
 * @param {string} message - The message to display.
 * @param {"success" | "error" | "info"} type - The type of toast (for styling).
 */
function showToast(message, type) {
    // Assuming a toast notification system is available (e.g., Bootstrap Toasts)
    // This is a placeholder. You might need to implement a proper toast display.
    console.log(`Toast (${type}): ${message}`);
    alert(message); // Fallback to alert for demonstration
}

class PaymentHandler {
    constructor() {
        this.paymentModal = document.getElementById("paymentModal") ? new bootstrap.Modal(document.getElementById("paymentModal")) : null;
        this.currentInvoiceId = null;
        this.elements = {
            paymentTotalAmount: document.getElementById("paymentTotalAmount"),
            paymentAmount: document.getElementById("paymentAmount"),
            balanceAfterPayment: document.getElementById("balanceAfterPayment"),
            processPaymentBtn: document.getElementById("processPaymentBtn"),
            transactionIdGroup: document.getElementById("transactionIdGroup"),
            transactionId: document.getElementById("transactionId"),
            paymentNotes: document.getElementById("paymentNotes"),
            paymentMethodRadios: document.querySelectorAll("input[name=\"paymentMethod\"]"),
        };

        this.initEventListeners();
    }

    initEventListeners() {
        if (this.paymentModal) {
            // Event listener for status select elements (e.g., on invoice list page)
            document.querySelectorAll(".status-select").forEach(select => {
                // Initialize prevValue on page load to the current value of the select element
                select.dataset.prevValue = select.value;
                select.addEventListener("change", this.handleStatusChange.bind(this));
            });

            // Event listener for processing payment button
            if (this.elements.processPaymentBtn) {
                this.elements.processPaymentBtn.addEventListener("click", this.processPayment.bind(this));
            }

            // Event listener for payment amount input to update balance display
            if (this.elements.paymentAmount) {
                this.elements.paymentAmount.addEventListener("input", this.updateBalanceDisplay.bind(this));
            }

            // Event listeners for payment method radios to show/hide transaction ID field
            this.elements.paymentMethodRadios.forEach(radio => {
                radio.addEventListener("change", this.handlePaymentMethodChange.bind(this));
            });
        }
    }

    /**
     * Handles the change event on invoice status select dropdowns.
     * @param {Event} event - The change event.
     */
    handleStatusChange(event) {
        const select = event.target;
        const invoiceId = select.dataset.invoiceId;
        const selectedValue = select.value; // New value user picked
        this.currentInvoiceId = invoiceId; // Store current invoice ID
    
        const totalAmount = parseFloat(select.dataset.totalAmount);
        let balanceDue = parseFloat(select.dataset.balanceDue || totalAmount);

        // Get the previous value from dataset, then update dataset.prevValue to the current selectedValue
        const prevValue = select.dataset.prevValue;
        select.dataset.prevValue = selectedValue;

        if (selectedValue === '1') { // Paid selected
            if (balanceDue > 0) {
                this.populatePaymentModal(balanceDue);
                this.paymentModal.show();
            } else {
                showToast('This invoice is already fully paid.', 'info');
                // Revert the select value if no action is taken (e.g., already paid)
                select.value = prevValue;
            }
        } else if (selectedValue === '0') { // Unpaid selected
            // Revert the select immediately, as the actual status change happens after modal confirmation
            select.value = prevValue;

            // Show your 'mark unpaid' modal here
            const markUnpaidModalElement = document.getElementById('markUnpaidModal');
            if (markUnpaidModalElement) {
                const markUnpaidModal = new bootstrap.Modal(markUnpaidModalElement);
            
                // Set the invoice ID in the hidden input
                document.getElementById('unpaidInvoiceId').value = invoiceId;
            
                // Reset modal inputs
                document.getElementById('unpaidReason').value = '';
                document.getElementById('confirmUnpaid').checked = false;
                document.getElementById('unpaidReasonCount').textContent = '0';
            
                // Show modal
                markUnpaidModal.show();
            
                // Optional: Store reference for future use
                this.pendingInvoiceSelect = select;
            }
            else {
                console.error('Mark Unpaid Modal element not found!');
                showToast('Error: Mark Unpaid Modal not found. Please refresh the page.', 'error');
            }
        }
    }

    /**
     * Populates the payment modal with relevant invoice data.
     * @param {number} balanceDue - The balance due for the invoice.
     */
    populatePaymentModal(balanceDue) {
        if (this.elements.paymentTotalAmount) {
            this.elements.paymentTotalAmount.textContent = `${balanceDue.toFixed(2)} RWF`;
        }
        if (this.elements.paymentAmount) {
            this.elements.paymentAmount.value = balanceDue.toFixed(2);
            this.elements.paymentAmount.max = balanceDue;
        }
        this.updateBalanceDisplay();
        // Reset transaction ID and notes fields
        if (this.elements.transactionId) this.elements.transactionId.value = '';
        if (this.elements.paymentNotes) this.elements.paymentNotes.value = '';
        // Default to cash payment method
        const cashRadio = document.getElementById('cashPayment');
        if (cashRadio) cashRadio.checked = true;
        this.handlePaymentMethodChange(); // Ensure transaction ID group is hidden initially
    }

    /**
     * Updates the displayed balance after payment based on input amount.
     */
    updateBalanceDisplay() {
        const currentBalance = parseFloat(this.elements.paymentTotalAmount.textContent.replace(' RWF', '')) || 0;
        const paymentAmount = parseFloat(this.elements.paymentAmount.value) || 0;
        const balanceAfter = Math.max(0, currentBalance - paymentAmount);
        if (this.elements.balanceAfterPayment) {
            this.elements.balanceAfterPayment.textContent = `${balanceAfter.toFixed(2)} RWF`;
        }
    }

    /**
     * Handles the change event for payment method radios, showing/hiding transaction ID field.
     */
    handlePaymentMethodChange() {
        const selectedMethod = document.querySelector('input[name="paymentMethod"]:checked')?.value;
        if (this.elements.transactionIdGroup && this.elements.transactionId) {
            if (selectedMethod !== 'CASH') {
                this.elements.transactionIdGroup.style.display = 'block';
                this.elements.transactionId.required = true;
            } else {
                this.elements.transactionIdGroup.style.display = 'none';
                this.elements.transactionId.required = false;
            }
        }
    }

    /**
     * Processes the payment by sending data to the backend API.
     */
    async processPayment() {
        const amount = parseFloat(this.elements.paymentAmount?.value) || 0;
        const methodInput = document.querySelector('input[name="paymentMethod"]:checked');
        const transactionId = this.elements.transactionId?.value;
        const notes = this.elements.paymentNotes?.value || '';

        if (!amount || amount <= 0) {
            showToast('Please enter a valid amount.', 'error');
            return;
        }

        if (!methodInput) {
            showToast('Please select a payment method.', 'error');
            return;
        }

        // Validate payment amount doesn't exceed balance due
        const select = document.querySelector(`.status-select[data-invoice-id="${this.currentInvoiceId}"]`);
        // Get the latest balanceDue from the dataset, which should be updated by the backend response
        const balanceDue = parseFloat(select?.dataset.balanceDue || select?.dataset.totalAmount || 0);
        
        if (amount > balanceDue) {
            showToast(`Payment amount cannot exceed remaining balance of ${balanceDue.toFixed(2)} RWF`, 'error');
            return;
        }

        this.setLoadingState(true);

        try {
            const response = await fetch(`/invoice/${this.currentInvoiceId}/pay/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    amount: amount,
                    method: methodInput.value,
                    transaction_id: transactionId,
                    notes: notes
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Payment failed with status:', response.status, 'Error response:', errorText);
                throw new Error(`Payment failed: ${errorText || response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.paymentModal.hide();
                this.updateInvoiceUI(data);
                showToast(data.message || 'Payment processed successfully!', 'success');
            } else {
                throw new Error(data.error || 'Payment failed.');
            }
        } catch (error) {
            console.error('Payment error:', error);
            showToast(error.message || 'Payment failed. Please try again.', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * Sets the loading state for the process payment button.
     * @param {boolean} isLoading - Whether to show loading spinner.
     */
    setLoadingState(isLoading) {
        const spinner = this.elements.processPaymentBtn?.querySelector('.spinner-border');
        const icon = this.elements.processPaymentBtn?.querySelector('.bi-check-circle');
        if (spinner) spinner.classList.toggle('d-none', !isLoading);
        if (icon) icon.classList.toggle('d-none', isLoading);
        if (this.elements.processPaymentBtn) this.elements.processPaymentBtn.disabled = isLoading;
    }

    /**
     * Updates the UI for the invoice after a successful payment.
     * @param {object} data - The response data from the payment API.
     */
    updateInvoiceUI(data) {
        const select = document.querySelector(`.status-select[data-invoice-id="${this.currentInvoiceId}"]`);
        if (select) {
            // Update the select value based on the new status
            // The backend now sends the correct 'status' string, use that directly
            // Map 'paid' to '1' and 'pending'/'partial' to '0' for the select element
            if (data.status === 'paid') {
                select.value = '1'; 
            } else if (data.status === 'partial' || data.status === 'pending') {
                select.value = '0'; 
            }
            // Update the dataset.balanceDue with the latest value from the backend
            select.dataset.balanceDue = data.balance_due;
            // Update the dataset.totalAmount if it's meant to reflect the initial total
            // or if it can change (less likely for totalAmount, but good to be aware)
            // select.dataset.totalAmount = data.total_amount; // Uncomment if total_amount can change

            // Update the prevValue to reflect the new, confirmed status from the backend
            select.dataset.prevValue = select.value;

            // Assuming updateStatusBadge is a function that visually updates the badge
            if (typeof updateStatusBadge === 'function') {
                updateStatusBadge(select);
            }
        }
    }
}

// Initialize the PaymentHandler when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaymentHandler();
});

// Placeholder for updateStatusBadge function - you need to define this based on your UI
function updateStatusBadge(selectElement) {
    // Example: Update a badge next to the select element
    const invoiceId = selectElement.dataset.invoiceId;
    const statusBadge = document.getElementById(`status-badge-${invoiceId}`); // Assuming you have such an ID
    if (statusBadge) {
        // Use the actual value from the select element, which is now updated by updateInvoiceUI
        if (selectElement.value === '1') {
            statusBadge.textContent = 'Paid';
            statusBadge.className = 'badge bg-success';
        } else if (selectElement.dataset.balanceDue > 0) {
            statusBadge.textContent = 'Partial'; // Or 'Pending' if no partial status
            statusBadge.className = 'badge bg-warning';
        } else {
            statusBadge.textContent = 'Pending';
            statusBadge.className = 'badge bg-secondary';
        }
    }



    // ////////// un paid form 
    const form = document.getElementById('markUnpaidForm');
    const modal = new bootstrap.Modal(document.getElementById('markUnpaidModal'));
    const submitBtn = document.getElementById('submitUnpaidBtn');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const invoiceId = document.getElementById('unpaidInvoiceId').value;
        const reason = document.getElementById('unpaidReason').value;
        const confirm = document.getElementById('confirmUnpaid').checked;

        if (!confirm || !reason.trim()) {
            showToast("You must confirm and provide a reason.", "warning");
            return;
        }

        // Show loading spinner
        submitBtn.querySelector('.spinner-border').classList.remove('d-none');
        submitBtn.setAttribute('disabled', 'true');

        fetch('/mark-unpaid/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                invoice_id: invoiceId,
                reason: reason,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Invoice marked as unpaid successfully.', 'success');
                modal.hide();
                // Optionally refresh page or update UI
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.message || 'Failed to mark unpaid.', 'danger');
            }
        })
        .catch(() => {
            showToast('Server error. Please try again.', 'danger');
        })
        .finally(() => {
            submitBtn.querySelector('.spinner-border').classList.add('d-none');
            submitBtn.removeAttribute('disabled');
        });
    });

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}





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