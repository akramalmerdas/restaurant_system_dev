/**
 * Integrated notification system for restaurant orders
 * Supports both PyWebView desktop mode and browser mode
 */

// Global variables
let currentNotificationAudio = null;
let soundEnabled = false;
let soundPermissionRequested = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_DELAY = 30000;
let isPyWebViewMode = false;

// Check if running in PyWebView
function checkPyWebViewMode() {
    try {
        isPyWebViewMode = window.pywebview !== undefined;
        console.log('PyWebView mode detected:', isPyWebViewMode);
    } catch (e) {
        isPyWebViewMode = false;
        console.log('Running in browser mode');
    }
}

// Connect to WebSocket for real-time notifications
function connectToNotifications() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/ws/notifications/`;

    console.log('Connecting to WebSocket:', wsUrl);

    try {
        const socket = new WebSocket(wsUrl);

        socket.onopen = function() {
            console.log('WebSocket connection established');
            reconnectAttempts = 0;
        };

        socket.onmessage = function(e) {
            console.log('Message received from WebSocket:', e.data);
            try {
                const data = JSON.parse(e.data);
                if (data.type === 'new_order') {
                    showOrderNotification(data);
                    if (window.location.pathname.includes('admin_dashboard') || window.location.pathname.includes('invoice_dashboard')) {
                        updateOrderList();
                    }
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };

        socket.onclose = function() {
            console.log('WebSocket connection closed');
            reconnectAttempts++;
            const delay = Math.min(3000 * Math.pow(1.5, reconnectAttempts - 1), MAX_RECONNECT_DELAY);
            console.log(`Reconnecting in ${delay/1000} seconds...`);
            setTimeout(connectToNotifications, delay);
        };

        socket.onerror = function(e) {
            console.error('WebSocket error:', e);
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
    }
}

// Show notification for new order
function showOrderNotification(data) {
    console.log('Showing notification for order:', data);

    if (!data || !data.order_id) {
        console.error('Invalid notification data');
        return;
    }

    // Create toast notification
    const notification = document.createElement('div');
    notification.className = 'toast show notification-toast';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.backgroundColor = '#fff';
    notification.style.boxShadow = '0 0.25rem 0.75rem rgba(0, 0, 0, 0.1)';
    notification.style.width = '350px';
    notification.style.maxWidth = '100%';
    notification.style.zIndex = '9999';

    const customerName = data.customer || 'Customer';
    const totalAmount = data.total ? `$${data.total}` : 'N/A';

    const orderViewUrl = document.body.dataset.orderViewUrl;
    notification.innerHTML = `
        <div class="toast-header bg-success text-white">
            <strong class="me-auto">New Order Received</strong>
            <small>${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close btn-close-white close-notification"></button>
        </div>
        <div class="toast-body">
            <p><strong>Order #${data.order_id}</strong> from ${customerName}</p>
            <p>Total: ${totalAmount}</p>
            <a href="${orderViewUrl.replace('0', data.order_id)}" class="btn btn-sm btn-primary view-order">View Order</a>
        </div>
    `;

    document.body.appendChild(notification);

    // Add event listeners
    const closeButton = notification.querySelector('.close-notification');
    closeButton.addEventListener('click', () => {
        notification.remove();
        stopNotificationSound();
    });

    const viewButton = notification.querySelector('.view-order');
    viewButton.addEventListener('click', () => {
        stopNotificationSound();
    });

    // Show desktop notification if not in PyWebView mode
    // (PyWebView already handles this with its own window)
    if (!isPyWebViewMode) {
        showDesktopNotification(data);
    }

    // Play notification sound
    playNotificationSound();
}

// Show desktop notification (browser mode only)
function showDesktopNotification(data) {
    if (!("Notification" in window)) {
        console.log("Browser doesn't support notifications");
        return;
    }

    if (Notification.permission === "granted") {
        createDesktopNotification(data);
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                createDesktopNotification(data);
            }
        });
    }
}

// Create desktop notification (browser mode only)
function createDesktopNotification(data) {
    try {
        const notification = new Notification("New Order Received", {
            body: `Order #${data.order_id} from ${data.customer || 'Customer'}\nTotal: ${data.total ? '$'+data.total : 'N/A'}`,
            icon: document.body.dataset.logoUrl,
            requireInteraction: true
        });

        notification.onclick = function() {
            window.focus();
            const orderViewUrl = document.body.dataset.orderViewUrl;
            window.location.href = orderViewUrl.replace('0', data.order_id);
            stopNotificationSound();
            this.close();
        };
    } catch (error) {
        console.error('Error creating desktop notification:', error);
    }
}

// Play notification sound - handles both PyWebView and browser modes
function playNotificationSound() {
    stopNotificationSound();

    if (isPyWebViewMode) {
        // Use PyWebView API
        try {
            console.log('Using PyWebView to play sound');
            window.pywebview.api.start_sound();
        } catch (e) {
            console.error('PyWebView sound API error:', e);
            playBrowserSound();
        }
    } else {
        // Use browser audio
        playBrowserSound();
    }
}

// Play sound using browser Audio API (fallback)
function playBrowserSound() {
    console.log('Using browser audio API');
    const audio = new Audio(document.body.dataset.ringtoneUrl);
    audio.loop = true;

    currentNotificationAudio = audio;

    audio.play().then(() => {
        soundEnabled = true;
        localStorage.setItem('notificationSoundEnabled', 'true');
    }).catch(e => {
        console.error('Failed to play sound:', e);
        currentNotificationAudio = null;

        if (!soundEnabled) {
            showSoundPermissionPrompt();
        }
    });
}

// Stop notification sound - handles both PyWebView and browser modes
function stopNotificationSound() {
    if (isPyWebViewMode) {
        // Use PyWebView API
        try {
            console.log('Using PyWebView to stop sound');
            window.pywebview.api.stop_sound_playback();
        } catch (e) {
            console.error('PyWebView sound API error:', e);
        }
    } else {
        // Use browser audio
        if (currentNotificationAudio) {
            console.log('Stopping browser audio');
            currentNotificationAudio.pause();
            currentNotificationAudio.currentTime = 0;
            currentNotificationAudio = null;
        }
    }
}

// Show sound permission prompt (browser mode only)
function showSoundPermissionPrompt() {
    // Don't show in PyWebView mode
    if (isPyWebViewMode) return;

    // Only show the prompt once per session
    if (soundPermissionRequested) return;
    soundPermissionRequested = true;

    console.log('Showing sound permission prompt');

    // Create a prominent message
    const prompt = document.createElement('div');
    prompt.id = 'sound-permission-prompt';
    prompt.style.position = 'fixed';
    prompt.style.top = '0';
    prompt.style.left = '0';
    prompt.style.right = '0';
    prompt.style.backgroundColor = '#f8d7da';
    prompt.style.color = '#721c24';
    prompt.style.padding = '1rem';
    prompt.style.textAlign = 'center';
    prompt.style.zIndex = '9999';
    prompt.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';

    prompt.innerHTML = `
        <strong>Important:</strong> Order notification sounds are disabled.
        <button class="btn btn-danger btn-sm mx-2">Click here to enable sounds</button>
        (required for order alerts)
    `;

    document.body.prepend(prompt);

    // Add click handler to the entire prompt
    prompt.addEventListener('click', (e) => {
        e.preventDefault();
        enableNotificationSound();
    });
}

// Enable notification sound (browser mode only)
function enableNotificationSound() {
    // Don't need this in PyWebView mode
    if (isPyWebViewMode) return;

    console.log('Enabling notification sound');

    const audio = new Audio(document.body.dataset.ringtoneUrl);
    audio.volume = 0.0;

    audio.play().then(() => {
        soundEnabled = true;
        localStorage.setItem('notificationSoundEnabled', 'true');

        const permissionPrompt = document.getElementById('sound-permission-prompt');
        if (permissionPrompt) {
            permissionPrompt.style.display = 'none';
        }

        const btn = document.getElementById('enable-sound-btn');
        if (btn) {
            btn.textContent = 'Sound Enabled';
            btn.classList.add('btn-success');
        }
    }).catch(e => {
        console.error('Sound could not be enabled:', e);
        showSoundPermissionPrompt();
    });
}

// Update order list via AJAX
function updateOrderList() {
    fetch(document.body.dataset.getOrdersUrl)
        .then(response => {
            if (!response.ok) throw new Error('HTTP error ' + response.status);
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('order-list-container');
            if (container) updateOrderListUI(data, container);
        })
        .catch(error => console.error('Error fetching orders:', error));
}

// Update order list UI
function updateOrderListUI(orders, container) {
    if (!orders || !orders.length) return;

    let html = '';
    const orderViewUrl = document.body.dataset.orderViewUrl;
    orders.forEach(order => {
        const statusClass = getStatusClass(order.status);
        html += `
            <div class="order-item" data-order-id="${order.id}">
                <div class="order-header">
                    <h5>Order #${order.id}</h5>
                    <span class="badge ${statusClass}">${order.status}</span>
                </div>
                <div class="order-details">
                    <p>Customer: ${order.customer}</p>
                    <p>Total: $${order.total}</p>
                    <p>Time: ${new Date(order.created_at).toLocaleString()}</p>
                </div>
                <div class="order-actions">
                    <a href="${orderViewUrl.replace('0', order.id)}" class="btn btn-sm btn-primary view-order">View</a>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Get status class based on order status
function getStatusClass(status) {
    switch(status?.toLowerCase()) {
        case 'completed': return 'bg-success';
        case 'processing': return 'bg-primary';
        case 'pending': return 'bg-warning';
        case 'cancelled': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// Test function to manually trigger a notification
function testNotification() {
    const testData = {
        type: 'new_order',
        order_id: '12345',
        customer: 'Test Customer',
        total: '42.99'
    };
    showOrderNotification(testData);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing notification system');

    // Check if running in PyWebView mode
    checkPyWebViewMode();

    // Connect to WebSocket
    connectToNotifications();

    // In browser mode, check if sound was previously enabled
    if (!isPyWebViewMode && localStorage.getItem('notificationSoundEnabled') === 'true') {
        enableNotificationSound();
    }

    // Set up sound enable button (browser mode only)
    if (!isPyWebViewMode) {
        const soundButton = document.getElementById('enable-sound-btn');
        if (soundButton) {
            soundButton.addEventListener('click', enableNotificationSound);
        }

        // Add document-level click handler for sound enablement
        if (localStorage.getItem('notificationSoundEnabled') === 'true' && !soundEnabled) {
            const enableSoundOnce = function() {
                enableNotificationSound();
                document.removeEventListener('click', enableSoundOnce);
            };
            document.addEventListener('click', enableSoundOnce);
        }
    }

    // Add test button if it exists
    const testButton = document.getElementById('test-notification-btn');
    if (testButton) {
        testButton.addEventListener('click', testNotification);
    }
});
