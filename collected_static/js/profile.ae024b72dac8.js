document.addEventListener("DOMContentLoaded", function() {
    const editButton = document.getElementById("edit-btn");
    const form = document.getElementById("profile-form");
  
    // Check if the editButton exists
    if (editButton && form) {
  
      const formElements = form.querySelectorAll("input, button[type='submit']");
  
      // Disable the form elements initially
      formElements.forEach(element => {
        element.disabled = true;
      });
  
      // Enable the form when the "Edit" button is clicked
      editButton.addEventListener("click", function() {
        console.log('I clicked the edit button');
        formElements.forEach(element => {
          element.disabled = false;
        });
  
      });
    } else {
      console.error("Edit button or form not found.");
    }
  });
  

  document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('profile-form');
    const editButton = document.getElementById('edit-btn');
    const updateButton = document.getElementById('update-profile-btn');
    const inputs = form.querySelectorAll('input');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Enable inputs for editing
    editButton.addEventListener('click', () => {
        inputs.forEach(input => input.disabled = false);
        updateButton.disabled = false;
    });

    // Handle form submission via AJAX
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to update profile');
            }
        })
        .then(data => {
            alert(data.message || 'Profile updated successfully!');
            inputs.forEach(input => input.disabled = true);
            updateButton.disabled = true;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the profile. Please try again.');
        });
    });
});
