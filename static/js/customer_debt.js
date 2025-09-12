document.addEventListener('DOMContentLoaded', function () {
    const paymentModal = document.getElementById('paymentModal');
    const customerSelectionModal = new bootstrap.Modal(document.getElementById('customerSelectionModal'));
    const payOnAccountBtn = document.getElementById('payOnAccountBtn');
    const confirmOnAccountBtn = document.getElementById('confirmOnAccountBtn');
    const customerSelect = document.getElementById('customerSelect');

    let currentInvoiceId = null;

    // This event is triggered when the payment modal is about to be shown
    paymentModal.addEventListener('show.bs.modal', function (event) {
        // The modal can be triggered by a button (with event.relatedTarget)
        // or programmatically from another script (like invoice.js).
        // We need to handle both cases to reliably get the invoice ID.

        let invoiceId = null;

        // Case 1: Triggered programmatically, ID is stored on the modal's dataset.
        if (paymentModal.dataset.invoiceId) {
            invoiceId = paymentModal.dataset.invoiceId;
        }

        // Case 2: Triggered by a button click, ID is on the button's dataset.
        const button = event.relatedTarget;
        if (button && button.getAttribute('data-invoice-id')) {
            invoiceId = button.getAttribute('data-invoice-id');
        }

        currentInvoiceId = invoiceId;
    });

    payOnAccountBtn.addEventListener('click', function () {
        // Hide the payment modal
        // const paymentModalInstance = bootstrap.Modal.getInstance(paymentModal);
        // paymentModalInstance.hide();

        // Show the customer selection modal
        customerSelectionModal.show();
        loadCustomers();
    });

    async function loadCustomers() {
        try {
            const response = await fetch('/users/api/get-customers/');
            if (!response.ok) {
                throw new Error('Failed to load customers');
            }
            const customers = await response.json();

            customerSelect.innerHTML = ''; // Clear existing options
            if (customers.length === 0) {
                customerSelect.innerHTML = '<option value="" selected disabled>No customers found. Please add one first.</option>';
                confirmOnAccountBtn.disabled = true; // Disable confirm button if no customers
            } else {
                customerSelect.innerHTML = '<option value="" selected disabled>Select a customer...</option>';
                customers.forEach(customer => {
                    const option = document.createElement('option');
                    option.value = customer.id;
                    option.textContent = customer.full_name;
                    customerSelect.appendChild(option);
                });
                confirmOnAccountBtn.disabled = false;
            }
        } catch (error) {
            console.error('Error loading customers:', error);
            customerSelect.innerHTML = '<option value="" selected disabled>Failed to load customers</option>';
        }
    }

    confirmOnAccountBtn.addEventListener('click', async function () {
        const selectedCustomerId = customerSelect.value;

        if (!selectedCustomerId) {
            customerSelect.classList.add('is-invalid');
            return;
        }
        customerSelect.classList.remove('is-invalid');

        const spinner = confirmOnAccountBtn.querySelector('.spinner-border');
        const icon = confirmOnAccountBtn.querySelector('i');

        spinner.classList.remove('d-none');
        icon.classList.add('d-none');
        confirmOnAccountBtn.disabled = true;

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch(`/payments/api/invoice/${currentInvoiceId}/assign-customer/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ customer_id: selectedCustomerId }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to assign customer');
            }

            const result = await response.json();

            // On success
            customerSelectionModal.hide();
            const paymentModalInstance = bootstrap.Modal.getInstance(paymentModal);
            if(paymentModalInstance) {
                paymentModalInstance.hide();
            }

            // Show a success message (e.g., using a toast or a simple alert)
            alert(result.message || 'Invoice successfully assigned to customer account.');
            location.reload();

        } catch (error) {
            console.error('Error assigning customer:', error);
            alert('Error: ' + error.message);
        } finally {
            spinner.classList.add('d-none');
            icon.classList.remove('d-none');
            confirmOnAccountBtn.disabled = false;
        }
    });
});
