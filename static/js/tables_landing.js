document.addEventListener('DOMContentLoaded', function() {
    const tablesContainer = document.getElementById('tables-container');
    const modal = new bootstrap.Modal(document.getElementById('tableModal'));

    function renderTables() {
        tablesContainer.innerHTML = '';
        window.tablesData.forEach(tableData => {
            const table = tableData.fields;
            const tableElement = document.createElement('div');
            tableElement.className = `table-card status-${table.status}`;
            tableElement.setAttribute('data-table-id', tableData.pk);

            tableElement.innerHTML = `
                <div class="table-header">
                    <span class="table-number">Table ${table.number}</span>
                    <span class="table-status">${table.status.replace('_', ' ')}</span>
                </div>
                <div class="table-body">
                    <p>Capacity: ${table.capacity}</p>
                    <p>Section: ${table.section}</p>
                </div>
                <div class="table-footer">
                    <button class="btn btn-order" onclick="goToMenu(event, ${tableData.pk})">Order</button>
                    <button class="btn btn-details" onclick="showDetails(event, ${tableData.pk})">Details</button>
                </div>
            `;
            tablesContainer.appendChild(tableElement);
        });
    }

    window.goToMenu = function(event, tableId) {
        event.stopPropagation();
        const setTableUrl = document.body.dataset.setTableNumberUrl;
        const menuUrl = document.body.dataset.menuUrl;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(setTableUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `table_number=${tableId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = menuUrl;
            } else {
                alert('Could not set table number. Please try again.');
            }
        });
    };

    window.showDetails = function(event, tableId) {
        event.stopPropagation();
        const tableData = window.tablesData.find(t => t.pk === tableId);
        if (tableData) {
            const table = tableData.fields;
            document.getElementById('modalTableNumber').textContent = table.number;
            document.getElementById('modalTableStatus').textContent = table.status;
            document.getElementById('modalTableCapacity').textContent = table.capacity;
            document.getElementById('modalTableSection').textContent = table.section;
            document.getElementById('modalTableActive').textContent = table.is_active ? 'Yes' : 'No';
            document.getElementById('modalTableHold').textContent = table.inHold ? 'Yes' : 'No';
            document.getElementById('modalTableCreated').textContent = new Date(table.created_at).toLocaleString();
            document.getElementById('modalTableModified').textContent = new Date(table.last_modified).toLocaleString();
            modal.show();
        }
    };

    window.refreshTables = function() {
        window.location.reload();
    }

    function updateTime() {
        const now = new Date();
        document.getElementById('currentTime').textContent = now.toLocaleTimeString();
    }

    renderTables();
    setInterval(updateTime, 1000);
    updateTime();
});