document.addEventListener('DOMContentLoaded', function() {
    // Print order functionality
    document.querySelectorAll('.btn-print').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const orderId = this.getAttribute('data-order-id');
            if (!orderId) {
                console.error('No order ID found');
                return;
            }
            
            // Open the print view for the order in a new tab
            const printWindow = window.open(`/print_order_view/${orderId}/`, '_blank');
            
            // Focus the new window (required for some browsers)
            if (printWindow) {
                printWindow.focus();
            }
        });
    });

    // Status change handler
    document.querySelectorAll('.status-option').forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const orderId = this.dataset.orderId;
            const newStatus = this.dataset.status;
            const statusBadge = document.querySelector('.status-badge');
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
            
            // Send AJAX request to update status
            fetch(`/update_order_status/${orderId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    'status': newStatus
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update status badge
                    statusBadge.className = 'status-badge';
                    statusBadge.innerHTML = getStatusBadgeHtml(newStatus);
                    
                    // Show success message
                    showAlert('Status updated successfully!', 'success');
                } else {
                    throw new Error(data.error || 'Failed to update status');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating status: ' + error.message, 'danger');
            })
            .finally(() => {
                // Reset button text
                this.innerHTML = originalText;
            });
        });
    });

    // Helper function to get status badge HTML with appropriate styling
    function getStatusBadgeHtml(status) {
        const statusConfig = {
            'Pending': { 
                icon: 'bi-clock',
                class: 'status-pending'
            },
            'Ready to Print': { 
                icon: 'bi-printer',
                class: 'status-ready-to-print'
            },
            'Printed': { 
                icon: 'bi-check-circle',
                class: 'status-printed'
            },
            'Served': { 
                icon: 'bi-cup-hot',
                class: 'status-served'
            },
            'Delivered': { 
                icon: 'bi-truck',
                class: 'status-delivered'
            },
            'Completed': { 
                icon: 'bi-check-all',
                class: 'status-completed'
            },
            'Printing': { 
                icon: 'bi-printer',
                class: 'status-printing'
            }
        };
        
        const config = statusConfig[status] || { icon: 'bi-info-circle', class: 'status-pending' };
        return `<span class="status-badge ${config.class}"><i class="bi ${config.icon}"></i> ${status}</span>`;
    }

    // Helper function to show alerts
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto dismiss after 3 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 3000);
    }

    // Cancel order functionality
    // Initialize the modal
    const deleteOrderModal = new bootstrap.Modal(document.getElementById('deleteOrderModal'));
    let currentOrderId = null;
  
    // Handle delete button clicks
    document.querySelectorAll('.btn-cancel').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            order_id = this.getAttribute('data-order-id');
            document.getElementById('orderIdToDelete').value = order_id;
            document.getElementById('deletionReason').value = ''; // Clear previous reason
            deleteOrderModal.show();
        });
    });
  
    // Handle confirm delete button click
    document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
        const reason = document.getElementById('deletionReason').value.trim();
        if (!reason) {
            alert('Please provide a reason for cancellation');
            return;
        }
  
        // Send the deletion request
        fetch(`/delete_order/${order_id}/`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')  // This will get the CSRF token from cookies
          },
          body: JSON.stringify({
              reason: reason
          })
      })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close the modal and refresh the page or update the UI
                deleteOrderModal.hide();
                location.reload(); // Or update the specific row in the table
            } else {
                alert('Failed to cancel order: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your request');
        });
    });
});

// Helper function to get CSRF token
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

// Add a toast container to the page if it doesn't exist
if (!document.getElementById('statusToast')) {
    const toastContainer = document.createElement('div');
    toastContainer.innerHTML = `
        <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
            <div id="statusToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">Status Updated</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body"></div>
            </div>
        </div>
    `;
    document.body.appendChild(toastContainer);
}
