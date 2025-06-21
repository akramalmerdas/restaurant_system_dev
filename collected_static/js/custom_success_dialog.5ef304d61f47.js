function showSuccessDialog(options = {}) {
    const modalElement = document.getElementById('customSuccessModal');
    if (!modalElement) {
        console.error('Custom Success Modal element not found in the DOM.');
        return;
    }

    // const modalTitle = modalElement.querySelector('#customSuccessModalLabel');
    const modalMessage = modalElement.querySelector('#customSuccessModalMessage');
    const modalOkButton = modalElement.querySelector('#customSuccessModalOkButton');

    // Set defaults and override with options
    // modalTitle.textContent = options.title || 'Success!';
    modalMessage.innerHTML = options.message || 'Operation completed successfully.'; // Use innerHTML to allow for HTML in message
    modalOkButton.textContent = options.okButtonText || 'OK';

    // Handle OK button click callback
    if (options.onOk && typeof options.onOk === 'function') {
        // Remove previous event listener to avoid multiple calls
        const newOkButton = modalOkButton.cloneNode(true);
        modalOkButton.parentNode.replaceChild(newOkButton, modalOkButton);
        newOkButton.addEventListener('click', function handleOk() {
            options.onOk();
            // Ensure the modal instance is available for hiding
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }, { once: true }); // Use { once: true } if the callback should only fire once per show
    }


    // Show the modal
    const successModal = new bootstrap.Modal(modalElement);
    successModal.show();

    // Optional: Auto-hide after a delay
    if (options.autoHideDelay && typeof options.autoHideDelay === 'number') {
        setTimeout(() => {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }, options.autoHideDelay);
    }
}