document.addEventListener('DOMContentLoaded', function() {
    initializeForms(); // Initialize all forms when the DOM is fully loaded
    
    // Add login form event listener
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent the default form submission

            const formData = new FormData(this); // Create a FormData object from the form
            const loadingElement = document.querySelector('.loading'); // Select the loading element

            // Show the loading indicator if it exists
            if (loadingElement) {
                loadingElement.style.display = 'block';
            }

            // Validate the form
            const isValid = validateForm(this);

            if (isValid) {
                try {
                    const response = await fetch('/login/', {
                        method: 'POST',
                        body: JSON.stringify({
                            email: formData.get('email'),
                            password: formData.get('password')
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    if (response.ok) {
                
                        window.location.href = data.redirect_url;
                    } else {
                        const data = await response.json();
                        alert(data.message || 'Login failed. Please check your credentials.');
                    }
                } catch (error) {
                    console.error('Error during login:', error);
                    alert('An unexpected error occurred. Please try again.');
                } finally {
                    // Hide the loading indicator
                    if (loadingElement) {
                        loadingElement.style.display = 'none';
                    }
                }
            }
        });
    }
});

function validateForm(form) {
    let isValid = true;
    
    // Get all required inputs
    const requiredInputs = form.querySelectorAll('[required]');
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) { // Check if the input is empty
            isValid = false; // Set isValid to false if any required field is empty
            showError(input, 'This field is required'); // Show an error message
        } else {
            removeError(input); // If the input is filled, remove any existing error message
            
            // Additional validation for email
            if (input.type === 'email') {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Regular expression for validating email
                if (!emailPattern.test(input.value)) { // Test the input value against the email pattern
                    isValid = false; // Set isValid to false if the email format is invalid
                    showError(input, 'Please enter a valid email address'); // Show an error message
                }   
            }
        }
    });
    
    const thisForm = form;
    const loadingElement = thisForm.querySelector('.loading');
    if (loadingElement) {
        loadingElement.classList.remove('d-block'); // Hide loading element if it exists
    } else {
        console.warn('Loading element not found'); // Log a warning if the loading element is not found
    }
    
    return isValid; // Return the overall validity of the form
}

function showError(input, message) {
    const formGroup = input.closest('.form-group');
    let errorDiv = formGroup.querySelector('.error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-danger mt-1';
        formGroup.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    input.classList.add('is-invalid');
}

function removeError(input) {
    const formGroup = input.closest('.form-group');
    const errorDiv = formGroup.querySelector('.error-message');
    
    if (errorDiv) {
        errorDiv.remove();
    }
    input.classList.remove('is-invalid');
}

function initializeForms() {
    const forms = document.querySelectorAll('form'); // Select all forms on the page
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) { // Validate the form before submission
                e.preventDefault(); // Prevent the default form submission if validation fails
            }
        });
    });
}

document.getElementById('signup-form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this); // Create a FormData object from the form
    const loadingElement = document.querySelector('.loading'); // Select the loading element

    // Show the loading indicator
    if (loadingElement) {
        loadingElement.style.display = 'block'; // Show loading
    }

    // Validate the form
    const isValid = validateForm(this); // Validate the form

    if (isValid) {
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        
        if (password !== confirmPassword) {
            alert('Passwords do not match!');
            showError(document.querySelector('input[name="confirm_password"]'), 'Passwords do not match');
            return;
        }

        try {
            const response = await fetch('/signup/', { // Send data to the signup endpoint
                method: 'POST',
                body: JSON.stringify({
                    name: formData.get('name'),
                    email: formData.get('email'),
                    phone_number: formData.get('phone_number'),
                    address: formData.get('address'),
                    password: password,
                    confirmPassword: confirmPassword
                }),
                headers: {
                    'Content-Type': 'application/json' // Set the content type to JSON
                }
            });
         
            if (response.ok) {
                const result = await response.json();
                alert(result.message);
                this.reset();
                setTimeout(() => {
          window.location.href = '/';
               }, 500); // Display success message
            } else {
                const error = await response.json();
                alert('Signup failed: ' + error.message); // Display error message
                showError(document.querySelector('input[name="email"]'), error.message); // Show error next to email input
            }
        } catch (error) {
            console.error('Error during signup:', error);
            alert('An unexpected error occurred. Please try again.'); // Handle network or other errors
        } finally {
            // Hide the loading indicator
            if (loadingElement) {
                loadingElement.style.display = 'none'; // Hide loading
            }
        }
    } else {
        // Hide the loading indicator if validation fails
        if (loadingElement) {
            loadingElement.style.display = 'none'; // Hide loading
        }
    }
});
