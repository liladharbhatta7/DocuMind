// Handle file input change (upload via click)
document.getElementById("file-input").addEventListener("change", uploadFile);

// Trigger file input when drop zone is clicked
document.getElementById("drop-zone").addEventListener("click", function() {
    document.getElementById("file-input").click();
});

// Drag-and-drop support
const dropZone = document.getElementById("drop-zone");
dropZone.addEventListener("dragover", function(e) {
    e.preventDefault();
    dropZone.style.backgroundColor = "#f9fafb";
});
dropZone.addEventListener("dragleave", function(e) {
    e.preventDefault();
    dropZone.style.backgroundColor = "";
});
dropZone.addEventListener("drop", function(e) {
    e.preventDefault();
    dropZone.style.backgroundColor = "";
    const file = e.dataTransfer.files[0];
    if (file) {
        uploadFile({ target: { files: [file] } });
    }
});

async function uploadFile(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("file", file);

        // Show loading message
        document.getElementById("loading").style.display = "block";
        document.getElementById("status-message").textContent = "";
        document.getElementById("output").textContent = "";

        try {
            // Send the file to the OCR endpoint
            const response = await fetch("/ocr", {
                method: "POST",
                body: formData
            });
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            const data = await response.json();
            // Display the extracted text
            document.getElementById("output").textContent = data.extracted_text;
            // Show the label selection area
            document.getElementById("label-container").style.display = "flex";
        } catch (error) {
            document.getElementById("output").textContent = "Error: " + error.message;
        } finally {
            document.getElementById("loading").style.display = "none";
        }
    }
}

// Add event listener for the Save button
document.getElementById("save-btn").addEventListener("click", async () => {
    // Get the extracted text and selected label
    const extractedText = document.getElementById("output").textContent;
    const label = document.getElementById("label-select").value;

    // Prepare data to send to backend
    const payload = { text: extractedText, label: label };

    try {
        // Send the payload to the /save endpoint via POST
        const response = await fetch("/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        const result = await response.json();
        document.getElementById("status-message").textContent = result.message;
    } catch (error) {
        document.getElementById("status-message").textContent = "Save Error: " + error.message;
    }
});
