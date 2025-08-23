"use strict";

const serverUrl = "http://127.0.0.1:8000";

async function uploadReceipt() {
  const fileInput = document.getElementById('receiptFile');
  const file = fileInput.files[0];
  let converter = new Promise(function(resolve, reject) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result
            .toString().replace(/^data:(.*,)?/, ''));
        reader.onerror = (error) => reject(error);
    });
    let encodedString = await converter;

    // clear file upload input field
    document.getElementById("receiptFile").value = "";

  if (!file) {
    alert("Please select a file to upload.");
    return;
  }

  try {
    return fetch(serverUrl + "/upload", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({filename: file.name, filebytes: encodedString})
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new HttpError(response);
        }
    })
  } catch (error) {
    console.error("Error during upload:", error);
    document.getElementById('result').textContent = `Error: Could not connect to the server. Please try again later.`;
  }
}