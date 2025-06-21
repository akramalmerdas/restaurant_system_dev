document.addEventListener('DOMContentLoaded', function () {
    var editOrderItemModal = document.getElementById('editOrderItemModal');
    editOrderItemModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var itemId = button.getAttribute('data-item-id');
        var quantity = button.getAttribute('data-quantity');
        var extrasRaw = button.getAttribute('data-extras');
        var itemName = button.getAttribute('data-item-name'); // Use plain JS to get the attribute
        // Set the item name in the modal (plain JS)
        var nameSpan = document.querySelector('.modal-item-name');
        if (nameSpan) {
            nameSpan.textContent = itemName;
        }
      
    
      
        // Parse extrasRaw into an array of objects with id field s
        let extras = [];
        if (extrasRaw && extrasRaw !== "None") {
            try {
                // Try to parse as JSON if possible
                extras = JSON.parse(extrasRaw);
               
                // If it's an array of ids, convert to array of objects
                if (Array.isArray(extras) && typeof extras[0] !== 'object') {
                    extras = extras.map(id => ({id: parseInt(id)}));
                }
            } catch (e) {
              
                // Fallback: comma-separated string of ids
                extras = extrasRaw.split(',').map(id => ({id: parseInt(id)}));
              
            }
        }

        // Build the orderItem object
        var orderItem = {
            item_id: itemId,
            quantity: quantity,
            extras: extras
        };

        // Call the helper to load extras and fill the modal
        openEditOrderItemModal(orderItem);
    });
});


// Helper: Open modal and load extras for the given item
function openEditOrderItemModal(orderItem) {
// Set item_id and quantity
document.getElementById('modal-item-id').value = orderItem.item_id;
document.getElementById('modal-quantity').value = orderItem.quantity;

// Fetch extras for this item
fetch(`/get-extras/${orderItem.item_id}/`)
.then(response => response.json())
.then(data => {

  // Populate extras checkboxes
  const extrasDiv = document.getElementById('modal-extras-checkboxes');
  extrasDiv.innerHTML = '';
  const selectedExtras = (orderItem.extras || []).map(e => e.id);
 
  (data.extras || []).forEach(extra => {
   
    const checked = selectedExtras.includes(extra.id) ? 'checked' : '';
    
    extrasDiv.innerHTML += `
      <div class="form-check">
        <input class="form-check-input" type="checkbox" value="${extra.id}" id="extra-${extra.id}" ${checked}>
        <label class="form-check-label" for="extra-${extra.id}">
          ${extra.name} (+${extra.price})
        </label>
      </div>
    `;
  });

}

);
}

// On form submit, collect checked extras and set hidden input
document.getElementById('edit-order-item-form').addEventListener('submit', function(e) {
const checked = Array.from(document.querySelectorAll('#modal-extras-checkboxes input[type="checkbox"]:checked'))
.map(cb => cb.value);
document.getElementById('modal-extras').value = checked.join(',');
});

//////////////////////////////// confirm order ///////////////////////
// const confirmButton = document.getElementById('confirm-order-btn');
// if (confirmButton){
//   confirmButton.addEventListener('click', async function() {

  
//     // Send a POST request to submit the order
//     try {
//    //    await printOrder();  

//         const response = await fetch('/submit_order/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': '{{ csrf_token }}'  // Include CSRF token if required
//             },
//             body: JSON.stringify({ items: JSON.parse(sessionStorage.getItem('order')) })  // Fetch order from sessionStorage
//         });
     
//          if (response.ok) {
//           console.log('the response is ok');
//           showSuccessDialog({
//             title: 'Success!',
//             message: 'the order was submitted successfully!',
//             okButtonText: 'OK',
//             onOk: function() {
          
//             setTimeout(() => {
//               window.location.href = '/';
//           }, 500);
//             },
//             // autoHideDelay: 10000 // Optional: auto-hide after 2 seconds
//         });   
//         }
//          else {
//             alert('Failed to submit the order. Please try again later.');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         alert('There was an error submitting your order.');
//     }
//   });
// }
//////////////////////////////////////// confirm order waiter edition /////////////
const confirmButton = document.getElementById('confirm-order-btn');
if (confirmButton){
  confirmButton.addEventListener('click', async function() {
 const tableNumber = sessionStorage.getItem('table_number');
console.log(tableNumber);
        if (tableNumber === null || tableNumber === 'null') {
                  
          showSuccessDialog({
            title: 'Error!',
            message: 'Table number is not set. Please set the table number before confirming the order',
            okButtonText: 'OK',
            onOk: function() {
              sessionStorage.removeItem('table_number');
            setTimeout(() => {

              return;
          }, 500);
            },
            // autoHideDelay: 10000 // Optional: auto-hide after 2 seconds
        }); 
           
        }
  
    // Send a POST request to submit the order
    try {
   //    await printOrder();  

        const response = await fetch('/submit_order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'  // Include CSRF token if required
            },
            body: JSON.stringify({ items: JSON.parse(sessionStorage.getItem('order')) })  // Fetch order from sessionStorage
        });
     
         if (response.ok) {
          console.log('the response is ok');
          showSuccessDialog({
            title: 'Success!',
            message: 'the order was submitted successfully!',
            okButtonText: 'OK',
            onOk: function() {
              sessionStorage.removeItem('table_number');
            setTimeout(() => {

              window.location.href = '/';
          }, 500);
            },
            // autoHideDelay: 10000 // Optional: auto-hide after 2 seconds
        });   
        }
         else {
            alert('Failed to submit the order. Please try again later.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error submitting your order.');
    }
  });
}

const emptyOrderButton = document.getElementById('empty-order-btn');
if (emptyOrderButton){

    // Add event listener to the button to handle the click event
    // This is just an example, you might need to adjust this based on your actual implementation
    // and how you want to clear the order inf
    emptyOrderButton.addEventListener('click', async function() {
      
        function getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
          }
        if (confirm('Are you sure you want to empty your cart ?')) {
           
        await fetch('/order_detail/empty_order/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCSRFToken(),
                },
              })
              .then(response => response.json())
              .then(data => {
                alert(data.message);
              });
              
        }
   
         window.location.reload();
    });
}



// Function to set the table number in session storage
function setTableNumber(tableNumber) {
    sessionStorage.setItem('table_number', tableNumber);
    console.log('Table number set to:', tableNumber);
}

// Event listener for the table selection dropdown
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired in order_details.js'); // Debugging log
    const tableSelect = document.getElementById('tableSelect');
    if (tableSelect) {
        console.log('tableSelect element found:', tableSelect); // Debugging log
        tableSelect.addEventListener('change', function() {
            console.log('Table selection changed. Value:', this.value); // Added for debugging
            setTableNumber(this.value);
        });
    } else {
        console.log('tableSelect element NOT found.'); // Debugging log
    }
});
