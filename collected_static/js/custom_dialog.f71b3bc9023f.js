export function showConfirmation(message, callback) {
    let confirmMessage = document.getElementById("confirmMessage");
    let dialog = document.getElementById("customDialog");

    if (!confirmMessage || !dialog) {
        console.error("Confirmation elements not found in the document.");
        return;
    }

    confirmMessage.textContent = message;
    dialog.style.display = "block";

    document.getElementById("confirmYes").onclick = function() {
        dialog.style.display = "none";
        callback(true);
    };

    document.getElementById("confirmNo").onclick = function() {
        dialog.style.display = "none";
        callback(false);
    };
}
