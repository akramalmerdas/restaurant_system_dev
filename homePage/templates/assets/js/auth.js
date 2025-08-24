// Function to get the CSRF token from the cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Add CSRF token to all AJAX requests that are not 'GET', 'HEAD', 'OPTIONS', 'TRACE'
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Override fetch to include the CSRF token
const originalFetch = window.fetch;
window.fetch = function (url, options) {
    options = options || {};
    // Only add the token for non-safe methods
    if (!csrfSafeMethod(options.method)) {
        options.headers = options.headers || {};
        // Only add the token if it's not already present
        if (!options.headers['X-CSRFToken']) {
            options.headers['X-CSRFToken'] = csrftoken;
        }
    }
    return originalFetch(url, options);
};


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
                    const loginUrl = document.body.dataset.loginUrl;
                    const adminDashboardUrl = document.body.dataset.adminDashboardUrl;
                    const response = await fetch(loginUrl, {
                        method: 'POST',
                        body: JSON.stringify({
                            email: formData.get('email'),
                            password: formData.get('password')
                        }),
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        // The server should redirect, but we can also do it client-side if needed
                        window.location.href = adminDashboardUrl; // Or wherever the user should go
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

    const signupForm = document.getElementById('signup-form');
    if(signupForm) {
        signupForm.addEventListener('submit', async function(event) {
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
                    if (loadingElement) {
                        loadingElement.style.display = 'none'; // Hide loading
                    }
                    return;
                }

                try {
                    const signupUrl = document.body.dataset.signupUrl;
                    const indexUrl = document.body.dataset.indexUrl;
                    const response = await fetch(signupUrl, { // Send data to the signup endpoint
                        method: 'POST',
                        body: JSON.stringify({
                            name: formData.get('name'),
                            email: formData.get('email'),
                            phone_number: formData.get('phone_number'),
                            address: formData.get('address'),
                            password: password
                        }),
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(result.message);
                        this.reset();
                        setTimeout(() => {
                            window.location.href = indexUrl;
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
