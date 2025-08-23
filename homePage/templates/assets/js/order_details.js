document.addEventListener('DOMContentLoaded', function () {
    var editOrderItemModal = document.getElementById('editOrderItemModal');
    editOrderItemModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var itemId = button.getAttribute('data-item-id');
        var quantity = button.getAttribute('data-quantity');
        var extrasRaw = button.getAttribute('data-extras');
        var itemName = button.getAttribute('data-item-name'); // Use plain JS to get the attribute
        var notes = button.getAttribute('data-notes') || '';
        document.getElementById('modal-notes').value = notes.trim();
        var row = button.getAttribute('data-row') || '';
        document.getElementById('modal-row').value = row;
     
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
          ${extra.name} (${extra.price} RWF)
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

const notes = document.getElementById('modal-notes').value.trim();
document.getElementById('modal-notes-hidden').value = notes;
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
 
        try {
          //    await printOrder();  
       
               const submitUrl = document.getElementById('confirm-order-btn').dataset.submitUrl;
               const response = await fetch(submitUrl, {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                       'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token if required
                   },
                   body: JSON.stringify({ items: JSON.parse(sessionStorage.getItem('order')) })  // Fetch order from sessionStorage
               });
            
                if (response.ok) {
               
                 showSuccessDialog({
                   title: 'Success!',
                   message: 'the order was submitted successfully!',
                   okButtonText: 'OK',
                   onOk: function() {
              //      sessionStorage.removeItem('table_number');
                   setTimeout(() => {
                    if (response.redirect_url) {
                      window.location.href = response.redirect_url;
                  } else {
                      // Fallback if no URL provided
                      window.location.href = '/table_landing/';
                  }
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
  
    // Send a POST request to submit the order
    
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



function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

// window.onload = function () {
//   const tableSelect = document.getElementById('tableSelect');
//   const savedTable = sessionStorage.getItem('table_number');
//   if (savedTable) {
//       tableSelect.value = savedTable;
//   }

//   tableSelect.addEventListener('change', function () {
//       setTableNumber(this.value);
//   });
// };
