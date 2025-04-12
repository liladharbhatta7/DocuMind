document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const extractedTextArea = document.getElementById("extracted-text");
    const predictionDiv = document.getElementById("prediction");

    // Open file dialog on drop zone click.
    dropZone.addEventListener("click", () => fileInput.click());

    // Handle drag events for visual feedback.
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = "#eef";
    });

    dropZone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = "";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = "";
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // When file is selected via file input.
    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    async function handleFile(file) {
        // Clear previous output.
        extractedTextArea.value = "";
        predictionDiv.innerText = "Processing...";

        const formData = new FormData();
        formData.append("file", file);

        try {
            // First, call the /ocr endpoint if you wish to display OCR output.
            // You can use the same /predict endpoint if that endpoint also returns the OCR text.
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            const data = await response.json();
            extractedTextArea.value = data.extracted_text || "";
            predictionDiv.innerText = `Prediction: ${data.prediction}`;
        } catch (error) {
            predictionDiv.innerText = `Error: ${error.message}`;
            console.error(error);
        }
    }
});
