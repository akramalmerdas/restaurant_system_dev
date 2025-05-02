// Import the confirmation dialog function (assuming it's reusable)
import { showConfirmation } from "./custom_dialog.js";

document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".btn-delete-item");

    deleteButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault(); // Prevent default button behavior

            const itemId = this.getAttribute("data-item-id");
            const itemName = this.getAttribute("data-item-name");
            const deleteUrl = `/items/${itemId}/delete/`; // Construct the URL based on your item app's urls.py

            showConfirmation(`Are you sure you want to delete the item "${itemName}"?`, function(confirmed) {
                if (confirmed) {
                    // Get CSRF token
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                    if (!csrfToken) {
                        console.error("CSRF token not found!");
                        alert("Error: Could not verify request security token.");
                        return;
                    }

                    // Perform the delete request using Fetch API
                    fetch(deleteUrl, {
                        method: "POST", // Django's DeleteView expects POST
                        headers: {
                            "X-CSRFToken": csrfToken,
                            "Content-Type": "application/json" // Optional, depending on view needs
                        },
                        // body: JSON.stringify({}) // Optional, depending on view needs
                    })
                    .then(response => {
                        // Check if redirect happened (DeleteView usually redirects on success)
                        if (response.redirected) {
                            window.location.href = response.url; // Follow redirect
                            return; // Stop processing
                        }
                        // If no redirect, check for JSON response (e.g., for errors)
                        return response.json().catch(() => ({})); // Attempt to parse JSON, default to empty object on failure
                    })
                    .then(data => {
                        if (data && data.message) { // Check for custom success message (if your view returns one)
                             alert(data.message);
                             location.reload(); // Or redirect as needed
                        } else if (data && data.error) { // Check for custom error message
                            alert(`Error: ${data.error}`);
                        } else {
                            // If DeleteView succeeded, we should have been redirected already.
                            // If we reach here without redirect, something might be wrong or the view behaves differently.
                            console.log("Delete action initiated. Expecting redirect or page reload.");
                            // Force reload if no redirect occurred but no explicit error was received
                            // location.reload();
                        }
                    })
                    .catch(error => {
                        console.error("Error during delete request:", error);
                        alert("An unexpected error occurred while trying to delete the item.");
                    });
                } else {
                    console.log("Item deletion cancelled.");
                }
            });
        });
    });
});