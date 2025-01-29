document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".btn-delete");
  
    buttons.forEach(button => {
      button.addEventListener("click", function (event) {
        console.log("Button clicked!"); // Debugging
    
        event.preventDefault(); // Prevent default behavior of the link/button
  
        const orderId = this.getAttribute("data-order-id"); // Get the order ID
        const confirmation = confirm("Are you sure you want to delete this order?");
        if (!confirmation) {
          return; // Exit if the user clicks "Cancel"
        }
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
