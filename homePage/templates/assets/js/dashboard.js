import { showConfirmation } from "./custom_dialog.js";

/////////////////////////////////delete order //////////////////////////////////////////
document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".btn-delete");
  
    buttons.forEach(button => {
      button.addEventListener("click", function (event) {
           
        event.preventDefault(); // Prevent default behavior of the link/button
  
        const orderId = this.getAttribute("data-order-id"); // Get the order ID
        showConfirmation("Do you want to delete this item?", function(confirmed) {
          if (confirmed) {
              const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // CSRF token
       
              fetch(`/delete_order/${orderId}/`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken // Pass the CSRF tokenl
                }
              })
              .then(response => response.json())
              .then(data => {
                if (data.message) {
                  alert(data.message); // Show success message
                  location.reload(); // Refresh the page
                } else if (data.error) {
                  alert(data.error); // Show error message
                }
              })
              .catch(error => {
                console.error("Error:", error);
                alert("An unexpected error occurred.");
              });
              // Execute the delete action here
          } else {
              alert("Action canceled.");
              return;
          }
      });
    
      });
    });
  });

  ///////////////////////////////// update order statues ///////////////////////////////////////////
  
  document.addEventListener("DOMContentLoaded", function () {
    const statusOptions = document.querySelectorAll(".status-option");

    statusOptions.forEach(option => {
        option.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default behavior of the link

            const orderId = this.getAttribute("data-order-id"); // Get the order ID
            const newStatus = this.getAttribute("data-status"); // Get the selected status
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // CSRF token

            fetch(`/update_order_status/${orderId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ status: newStatus }) // Send the new status
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Order status updated successfully!");
                    location.reload(); // Reload the page to reflect the updated status
                } else {
                    alert(data.error || "Failed to update order status.");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An unexpected error occurred.");
            });
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.btn-print-order').forEach(button => {
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
});