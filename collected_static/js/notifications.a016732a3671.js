// Connect to WebSocket for order notifications
function connectToNotifications() {
    // Determine the correct WebSocket protocol (ws:// or wss://)
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/ws/notifications/`;
    
    const notificationSocket = new WebSocket(wsUrl);
    
    notificationSocket.onopen = function(e) {
        console.log('Notification connection established');
    };
    
    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        
        if (data.type === 'new_order') {
            // Check if we need to refresh the page first
            if (window.location.pathname.includes('admin_dashboard')) {
                // Store the notification data in localStorage before refreshing
                localStorage.setItem('pendingNotification', JSON.stringify(data));
                // Refresh the page
                location.reload();
            } else {
                // If not on admin dashboard, just show the notification
                showOrderNotification(data);
            }
        }
    };
    
    notificationSocket.onclose = function(e) {
        console.log('Notification connection closed');
        // Try to reconnect after a delay
        setTimeout(function() {
            connectToNotifications();
        }, 3000);
    };
    
    notificationSocket.onerror = function(e) {
        console.error('Notification socket error:', e);
    };
}

// Add this at the end of the file, just before the last two lines
// Check for pending notifications when the page loads
document.addEventListener('DOMContentLoaded', function() {
    connectToNotifications();
    
    // Check if there's a pending notification from before the page refresh
    const pendingNotification = localStorage.getItem('pendingNotification');
    if (pendingNotification) {
        // Clear the pending notification from localStorage
        localStorage.removeItem('pendingNotification');
        // Show the notification
        showOrderNotification(JSON.parse(pendingNotification));
    }
});
function showOrderNotification(data) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'toast show';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#fff';
    notification.style.boxShadow = '0 0.25rem 0.75rem rgba(0, 0, 0, 0.1)';
    notification.style.width = '350px';
    notification.style.maxWidth = '100%';
    notification.style.zIndex = '9999';
    
    notification.innerHTML = `
        <div class="toast-header bg-success text-white">
            <strong class="me-auto">New Order Received</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <div class="toast-body">
            <p><strong>Order #${data.order_id}</strong> from ${data.customer}</p>
            <p>Total: $${data.total}</p>
            <a href="/order_view/${data.order_id}/" class="btn btn-sm btn-primary">View Order</a>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Play notification sound if available
    const audio = new Audio('/static/sounds/notification.mp3');
    audio.play().catch(e => console.log('Audio play failed:', e));
    
    // Remove the setTimeout that automatically removes the notification
    // The notification will now stay until the user clicks the close button
}

function updateOrderList() {
    // Use AJAX to update the order list without refreshing the page
    fetch('/get_orders/')
        .then(response => response.json())
        .then(data => {
            // Update the order list in the DOM
            const orderListContainer = document.getElementById('order-list-container');
            if (orderListContainer) {
                // Assuming you have a container with this ID to update
                updateOrderListUI(data, orderListContainer);
            }
        })
        .catch(error => console.error('Error fetching orders:', error));
}

function updateOrderListUI(orders, container) {
    // This function would update the UI with the new orders
    // The implementation depends on your HTML structure
    // This is just a placeholder example
    if (orders && orders.length > 0) {
        // Update the UI with the new orders
        // This will depend on your specific HTML structure
    }
}