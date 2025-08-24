document.addEventListener('DOMContentLoaded', function() {
    const saveItemBtn = document.getElementById('saveItemBtn');
    const itemForm = document.getElementById('itemForm');
    const itemImageInput = document.getElementById('itemImage');
    const currentImageContainer = document.getElementById('currentImageContainer');
    const currentImage = document.getElementById('currentImage');

    // Show preview of selected image
    if (itemImageInput) {
        itemImageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImage.src = e.target.result;
                    currentImage.alt = file.name;
                    currentImageContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                currentImageContainer.style.display = 'none';
            }
        });
    }

    // Save button logic
    if (saveItemBtn) {
        saveItemBtn.addEventListener('click', function() {
            // Simple validation
            const name = document.getElementById('itemName').value.trim();
            const price = document.getElementById('itemPrice').value.trim();

            if (!name || !price) {
                alert('Please fill in all required fields.');
                return;
            }

            // Confirmation dialog
            // if (confirm('Are you sure you want to save this item?')) {
            //     // For demo: just alert and reset form
            //     alert('Item saved!');
            //     itemForm.reset();
            //     currentImageContainer.style.display = 'none';
            // }
        });
    }
});