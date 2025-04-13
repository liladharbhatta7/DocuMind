// Global variable to store the extracted texts.
let extractedData = {};

// Event listener for the Extract button.
document.getElementById('extractBtn').addEventListener('click', async () => {
  const frontInput = document.getElementById('citizenshipFront');
  const backInput = document.getElementById('citizenshipBack');
  const statusMsgDiv = document.getElementById('statusMsg');

  // Clear previous status and global data
  statusMsgDiv.textContent = "";
  extractedData = {};

  // Ensure both files are selected
  if (frontInput.files.length === 0 || backInput.files.length === 0) {
    alert("Please upload both citizenship front and back images.");
    return;
  }

  // Prepare the form data with both files
  const formData = new FormData();
  formData.append("citizenship_front", frontInput.files[0]);
  formData.append("citizenship_back", backInput.files[0]);

  // Show processing message during extraction
  statusMsgDiv.textContent = "Extraction processing...";

  try {
    const response = await fetch("/extract", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Failed to extract text");
    }

    const data = await response.json();
    // Save extracted data for later processing
    extractedData = data;

    // Replace extracted text with a simple status message.
    statusMsgDiv.textContent = "Extraction complete!";
  } catch (error) {
    statusMsgDiv.textContent = "Error during extraction: " + error.message;
  }
});

// Event listener for the Process Text button.
document.getElementById('processTextBtn').addEventListener('click', async () => {
  const statusMsgDiv = document.getElementById('statusMsg');

  // Verify that OCR extraction has already been done.
  if (!extractedData.citizenship_front || !extractedData.citizenship_back) {
    alert("Please extract the text first.");
    return;
  }

  // Prepare JSON payload with extracted text.
  const payload = {
    citizenship_front: extractedData.citizenship_front,
    citizenship_back: extractedData.citizenship_back
  };

  // Show processing message during text processing
  statusMsgDiv.textContent = "Processing text...";

  try {
    const response = await fetch("/process_text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error("Failed to process text");
    }

    const data = await response.json();

    statusMsgDiv.textContent = "Processing complete! Form updated.";

    // Auto-fill form fields using the processed data:
    // Processed front information
    if (data.front_processed["Name (Nepali)"]) {
      document.getElementById('nameNepali').value = data.front_processed["Name (Nepali)"];
    }
    if (data.front_processed["Father's Name (Nepali)"]) {
      document.getElementById('fatherNameNepali').value = data.front_processed["Father's Name (Nepali)"];
    }
    // Processed back information
    if (data.back_processed["Full Name (English)"]) {
      document.getElementById('fullNameEn').value = data.back_processed["Full Name (English)"];
    }
    if (data.back_processed["Date of Birth"]) {
      document.getElementById('dob').value = data.back_processed["Date of Birth"];
    }
    if (data.back_processed["Permanent Address"]) {
      document.getElementById('permanentAddress').value = data.back_processed["Permanent Address"];
    }
    if (data.back_processed["Sex (English)"]) {
      // The returned value will already be in the format "Sex:Male"
      document.getElementById('sex').value = data.back_processed["Sex (English)"];
    }
    if (data.back_processed["Issuer Officer Name (Nepali)"]) {
      document.getElementById('issuerOfficer').value = data.back_processed["Issuer Officer Name (Nepali)"];
    }
    if (data.back_processed["Issuer Date (Nepali)"]) {
      document.getElementById('issuerDate').value = data.back_processed["Issuer Date (Nepali)"];
    }
  } catch (error) {
    statusMsgDiv.textContent = "Error during processing: " + error.message;
  }
});
