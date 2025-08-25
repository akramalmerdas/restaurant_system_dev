// ==== [ Helper Functions ] ==== //

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(`${name}=`)) {
            return decodeURIComponent(cookie.slice(name.length + 1));
        }
    }
    return null;
}

function getTableCardClass(table) {
    if (!table.is_active) return 'table-inactive';
    if (table.inHold) return 'table-hold';
    return `table-${table.status}`;
}

function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close ms-auto" onclick="this.closest('.alert').remove()"></button>
        </div>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// ==== [ Table Generation ] ==== //

function generateTables() {
    const tablesContainer = document.getElementById('tables-container');
    tablesContainer.innerHTML = '';

    const grid = document.createElement('div');
    grid.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4';
    grid.id = 'tables-grid';
    tablesContainer.appendChild(grid);

    (window.tablesData || []).forEach(data => {
        const table = {
            id: data.pk,
            ...data.fields,
            status: data.fields.status || 'available',
            capacity: data.fields.capacity || 4,
            section: data.fields.section || 'Main',
            last_modified: data.fields.updated_at || data.fields.created_at || new Date().toISOString()
        };

        const card = document.createElement('div');
        card.className = 'col';
        const statusDisplay = capitalize(table.status);

        card.innerHTML = `
            <div class="table-card ${getTableCardClass(table)}" onclick="openTableModal('${table.number}')" title="Click to manage table">
                <div class="table-number">Table ${table.number}</div>
                <div class="table-info"><i class="fas fa-users me-2"></i>Capacity: ${table.capacity} guests</div>
                <div class="d-flex justify-content-between align-items-center">
                    <span class="status-badge badge-${table.status}">${statusDisplay}</span>
                </div>
                ${table.inHold ? '<div class="status-indicator"><span class="status-dot dot-hold"></span>On Hold</div>' : ''}
                ${!table.is_active ? '<div class="status-indicator"><span class="status-dot dot-inactive"></span>Inactive</div>' : ''}
                <div class="table-meta">
                    <small><i class="fas fa-clock me-1"></i>Modified: ${new Date(table.last_modified).toLocaleString()}</small>
                </div>
                <div class="action-buttons">
                    <button class="btn-order" onclick="event.stopPropagation(); setTableNumber('${table.number}')">
                        <i class="fas fa-pen me-1"></i>Order
                    </button>
                    <button class="btn-status" onclick="event.stopPropagation(); getOrderByTable('${table.id}')">
                        Status <i class="fas fa-caret-down ms-1"></i>
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// ==== [ Modal Management ] ==== //

// function openTableModal(tableNumber) {
//     const table = (window.tablesData || []).find(t => t.fields.number === tableNumber);
//     if (!table) return;

//     const fields = table.fields;

//     document.getElementById('modalTableNumber').textContent = fields.number;
//     document.getElementById('modalTableStatus').innerHTML = `
//         <span class="status-badge badge-${fields.status}">
//             ${capitalize(fields.status)}
//         </span>
//     `;
//     document.getElementById('modalTableCapacity').textContent = fields.capacity;
//     document.getElementById('modalTableSection').textContent = fields.section || 'Main';
//     document.getElementById('modalTableActive').innerHTML = fields.is_active ?
//         '<span class="text-success"><i class="fas fa-check-circle"></i> Yes</span>' :
//         '<span class="text-danger"><i class="fas fa-times-circle"></i> No</span>';
//     document.getElementById('modalTableHold').innerHTML = fields.inHold ?
//         '<span class="text-warning"><i class="fas fa-pause-circle"></i> Yes</span>' :
//         '<span class="text-success"><i class="fas fa-play-circle"></i> No</span>';
//     document.getElementById('modalTableCreated').textContent = new Date(fields.created_at).toLocaleString();
//     document.getElementById('modalTableModified').textContent = new Date(fields.updated_at || fields.created_at).toLocaleString();

//     const modal = new bootstrap.Modal(document.getElementById('tableModal'));
//     modal.show();
// }

// ==== [ Set Table for Order ] ==== //

function setTableNumber(tableNumber) {
    const buttons = document.querySelectorAll('.btn-order');
    console.log('here we enterd the set tables function');
    buttons.forEach(btn => {
        if (btn.innerHTML.includes(`Table ${tableNumber}`)) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        }
    });

    const formData = new FormData();
    formData.append('table_number', tableNumber);

    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken);
    }

    fetch(document.body.dataset.setTableNumberUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Table ${tableNumber} selected successfully!`, 'success');
            window.location.href = document.body.dataset.menuUrl;
        } else {
            showNotification('Error: ' + (data.message || 'Failed to select table'), 'error');
        }
    })
    .catch(error => {
        console.error('Network error:', error);
        showNotification('Network error. Please try again.', 'error');
    })
    .finally(() => {
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-pen me-1"></i>Order';
        });
    });
}

// ==== [ Utility ] ==== //

function updateCurrentTime() {
    const now = new Date();
    const options = {
        weekday: 'long', year: 'numeric', month: 'long',
        day: 'numeric', hour: 'numeric', minute: 'numeric',
        second: 'numeric', hour12: true
    };
    document.getElementById('currentTime').textContent = now.toLocaleString('en-US', options);
}

function refreshTables() {
    const refreshIcon = document.querySelector('.refresh-btn i');
    refreshIcon.style.animation = 'spin 1s linear infinite';

    setTimeout(() => {
        window.location.reload();  // You can change to generateTables() if using SPA behavior
        refreshIcon.style.animation = '';
    }, 1000);
}

// ==== [ Initial Load ] ==== //

document.addEventListener('DOMContentLoaded', () => {
    generateTables();
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
});


function getOrderByTable(tableId) {
    if (!tableId) {
        alert("Invalid table ID");
        return;
    }
    const urlTemplate = document.body.dataset.getOrderByTableUrlTemplate;
    const url = urlTemplate.replace('0', tableId);
    // Open in a new tab (can change to modal or fetch later)
    window.location.href=url;
}
