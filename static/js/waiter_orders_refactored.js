// Streamlined Table Transfer and Filter JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tableFilter = document.getElementById('tableFilter');
    const targetTableSelect = document.getElementById('targetTableSelect');
    const moveSelectedBtn = document.getElementById('moveSelectedBtn');
    const selectionCounter = document.getElementById('selectionCounter');
    const selectedCount = document.getElementById('selectedCount');
    const transferAlertArea = document.getElementById('transferAlertArea');


    // ===== AUTOMATIC TABLE FILTERING =====

    // Make table filter automatic (no submit button needed)
    if (tableFilter) {
        tableFilter.addEventListener('change', function() {
            const selectedTableId = this.value;
            const currentUrl = new URL(window.location);

            if (selectedTableId) {
                currentUrl.searchParams.set('table_id', selectedTableId);
            } else {
                currentUrl.searchParams.delete('table_id');
            }

            // Navigate to the new URL automatically
            window.location.href = currentUrl.toString();
        });
    }

    // ===== ORDER SELECTION AND TRANSFER =====

    // Update selection counter and button states
    function updateSelectionState() {
        const selectedItems = document.querySelectorAll('.item-checkbox:checked');
        const count = selectedItems.length;

        if (selectedCount) {
            selectedCount.textContent = count;
        }

        if (selectionCounter) {
            selectionCounter.style.display = count > 0 ? 'flex' : 'none';
        }

        const targetSelected = targetTableSelect ? targetTableSelect.value : false;
        if (moveSelectedBtn) {
            moveSelectedBtn.disabled = !targetSelected;
        }

        // Update visual feedback for selected items
        document.querySelectorAll('.order-item').forEach(item => {
            const checkbox = item.querySelector('.item-checkbox');
            if (checkbox && checkbox.checked) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    // Show alert message
    function showAlert(message, type = 'success') {
        if (!transferAlertArea) return;

        const alertDiv = document.createElement('div');
        alertDiv.className = `transfer-alert alert-${type}`;
        alertDiv.textContent = message;
        transferAlertArea.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // MODIFIED: Get all order IDs from the current table instead of selected item IDs
    function getAllOrderIds() {
        const orderCards = document.querySelectorAll('.order-card');
        return Array.from(orderCards).map(card => card.getAttribute('data-order-id'));
    }


    // Transfer orders function
    async function transferOrders(orderIds, targetTableId, actionDescription = "transfer orders") {
        if (!orderIds || orderIds.length === 0) {
            showAlert('No orders available for transfer', 'danger');
            return false;
        }

        if (!targetTableId) {
            showAlert('Please select a target table', 'danger');
            return false;
        }
        console.log(window.location.href);
        try {
            fetch('/move_table_view/', { // <-- Use the new URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',

            'X-CSRFToken': getCsrfToken()// Ensure you have this helper function
        },
        // 3. Send ONLY the table_id. The server will do the rest.
        body: JSON.stringify({
            target_table_id: targetTableId,
            order_select: orderIds
        })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 200 && body.success) {
            alert(body.message || 'Orders moved successfully!');
            // Redirect to a fresh page after success
            setTimeout(() => {
                window.location.reload();
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
        } catch (error) {
            showAlert(`An error occurred during ${actionDescription}`, 'danger');
            console.error('Transfer error:', error);
            return false;
        }
    }

    // ===== EVENT LISTENERS =====

    // Listen for checkbox changes
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('item-checkbox')) {
            updateSelectionState();
        }
    });

    // Listen for target table selection changes
    if (targetTableSelect) {
        targetTableSelect.addEventListener('change', updateSelectionState);
    }

    // MODIFIED: Move selected orders button - now gets ALL order IDs
    if (moveSelectedBtn) {
        moveSelectedBtn.addEventListener('click', async function() {
            const allOrderIds = getAllOrderIds(); // Changed from getSelectedOrderIds()
            const targetTableId = targetTableSelect ? targetTableSelect.value : null;

            this.classList.add('loading');
            await transferOrders(allOrderIds, targetTableId, "transfer all orders from table");
            this.classList.remove('loading');
        });
    }

    // Initialize state
    updateSelectionState();

    // ===== GLOBAL FUNCTIONS FOR HTML ONCLICK HANDLERS =====

    // Make functions globally available
    window.toggleAllItems = function(selectAll) {
        const checkboxes = document.querySelectorAll('.item-checkbox');
        checkboxes.forEach(cb => cb.checked = selectAll);

        // Trigger change event to update UI
        const event = new Event('change', { bubbles: true });
        if (checkboxes.length > 0) {
            checkboxes[0].dispatchEvent(event);
        }
    };

    window.showQuickTransfer = function(itemId) {
        const dropdown = document.getElementById(`quickTransfer_${itemId}`);
        if (dropdown) {
            dropdown.style.display = 'block';
        }
    };

    window.hideQuickTransfer = function(itemId) {
        const dropdown = document.getElementById(`quickTransfer_${itemId}`);
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    };

    window.quickTransferItem = async function(itemId) {
        const targetSelect = document.getElementById(`quickTarget_${itemId}`);
        const targetTableId = targetSelect ? targetSelect.value : null;

        if (!targetTableId) {
            showAlert('Please select a target table', 'warning');
            return;
        }

        const success = await transferOrders([itemId], targetTableId, `transfer item #${itemId}`);
        if (success) {
            window.hideQuickTransfer(itemId);
        }
    };

    // Helper function to get CSRF token
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }

        // Alternative method from cookies
        const name = 'csrftoken';
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
        return cookieValue || '';
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+A to select all items
    if (e.ctrlKey && e.key === 'a' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        if (typeof window.toggleAllItems === 'function') {
            window.toggleAllItems(true);
        }
    }

    // Escape to clear selection and hide dropdowns
    if (e.key === 'Escape') {
        if (typeof window.toggleAllItems === 'function') {
            window.toggleAllItems(false);
        }

        // Hide any open quick transfer dropdowns
        document.querySelectorAll('.quick-transfer-dropdown').forEach(dropdown => {
            dropdown.style.display = 'none';
        });
    }
});
