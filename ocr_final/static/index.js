// Global variable to store the extracted texts.
let extractedData = {};

// Event listener for the Extract button.
document.getElementById('extractBtn').addEventListener('click', async () => {
  const frontInput = document.getElementById('citizenshipFront');
  const backInput = document.getElementById('citizenshipBack');
  const resultDiv = document.getElementById('result');
  const processedResultDiv = document.getElementById('processedResult');
  const loadingDiv = document.getElementById('loading');

  // Clear previous results
  resultDiv.textContent = "";
  processedResultDiv.textContent = "";
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

  // Display processing message
  loadingDiv.style.display = "block";

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

    // Format and display the extracted text from both images
    let output = "----- Extracted OCR Text (Front) -----\n" + data.citizenship_front +
      "\n\n----- Extracted OCR Text (Back) -----\n" + data.citizenship_back;
    resultDiv.textContent = output;
  } catch (error) {
    resultDiv.textContent = "Error: " + error.message;
  } finally {
    loadingDiv.style.display = "none";
  }
});

// Event listener for the Process Text button.
document.getElementById('processTextBtn').addEventListener('click', async () => {
  const processedResultDiv = document.getElementById('processedResult');
  const loadingDiv = document.getElementById('loading');

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

  // Display processing message
  loadingDiv.style.display = "block";

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

    // Format the processed results for display.
    let processedOutput = "----- Processed Front Information -----\n";
    for (let key in data.front_processed) {
      processedOutput += `${key}: ${data.front_processed[key]}\n`;
    }
    processedOutput += "\n----- Processed Back Information -----\n";
    for (let key in data.back_processed) {
      processedOutput += `${key}: ${data.back_processed[key]}\n`;
    }
    processedResultDiv.textContent = processedOutput;

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
      // Remove the "Sex:" prefix if needed (or leave it as is, based on your design)
      document.getElementById('sex').value = data.back_processed["Sex (English)"].replace("Sex:", "Sex:");
    }
    if (data.back_processed["Issuer Officer Name (Nepali)"]) {
      document.getElementById('issuerOfficer').value = data.back_processed["Issuer Officer Name (Nepali)"];
    }
    if (data.back_processed["Issuer Date (Nepali)"]) {
      document.getElementById('issuerDate').value = data.back_processed["Issuer Date (Nepali)"];
    }
    
  } catch (error) {
    processedResultDiv.textContent = "Error: " + error.message;
  } finally {
    loadingDiv.style.display = "none";
  }
});
