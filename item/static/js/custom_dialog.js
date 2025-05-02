window.showCustomDialog = function({title, message, type='info', showCancel=false, onOk=null, onCancel=null}) {
    const overlay = document.getElementById('customDialogOverlay');
    const header = document.getElementById('customDialogHeader');
    const body = document.getElementById('customDialogBody');
    const okBtn = document.getElementById('customDialogOk');
    const cancelBtn = document.getElementById('customDialogCancel');

    // Set dialog type styles
    header.style.background = type === 'success' ? '#d1e7dd'
                            : type === 'warning' ? '#fff3cd'
                            : type === 'danger' ? '#f8d7da'
                            : '#f1f1f1';
    header.style.color = type === 'danger' ? '#842029'
                          : type === 'warning' ? '#664d03'
                          : type === 'success' ? '#0f5132'
                          : '#222';

    header.textContent = title || '';
    body.textContent = message || '';
    cancelBtn.style.display = showCancel ? '' : 'none';

    overlay.style.display = 'block';

    function closeDialog() {
        overlay.style.display = 'none';
        okBtn.onclick = null;
        cancelBtn.onclick = null;
    }

    okBtn.onclick = function() {
        closeDialog();
        if (typeof onOk === 'function') onOk();
    };
    cancelBtn.onclick = function() {
        closeDialog();
        if (typeof onCancel === 'function') onCancel();
    };
};