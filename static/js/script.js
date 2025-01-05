document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const processBtn = document.getElementById('process-btn');
    const resetBtn = document.getElementById('reset-btn');
    
    const uploadSection = document.getElementById('upload-section');
    const textSection = document.getElementById('text-section');
    const processedSection = document.getElementById('processed-section');
    
    const originalData = document.getElementById('original-data');
    const processedData = document.getElementById('processed-data');
    const decodedSection = document.getElementById('decoded-section');
    const decodedData = document.getElementById('decoded-data');
    const decodeBtn = document.getElementById('decode-btn');

    let currentText = ''; // Store the current text being processed
    let isFromFile = false; // Track if text is from file upload or sample

    function showProcessingDescription() {
        const descriptionElement = document.getElementById('process-description');
        const description = `
            <strong>Processing Operations:</strong>
            <ul>
                <li>Tokenization of text using Byte Pair Encoding (BPE)</li>
                <li>Conversion to numerical token IDs</li>
            </ul>
        `;
        
        descriptionElement.innerHTML = description;
        descriptionElement.classList.remove('hidden');
    }

    // Upload button click handler
    uploadBtn.addEventListener('click', () => fileInput.click());

    // File input change handler
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            // Clear previous data
            originalData.innerHTML = '';
            processedData.innerHTML = '';
            decodedData.innerHTML = '';  // Clear decoded data
            
            // Clear descriptions and hide sections
            document.getElementById('process-description').innerHTML = '';
            document.getElementById('process-description').classList.add('hidden');
            processedSection.classList.add('hidden');
            decodedSection.classList.add('hidden');  // Hide decoded section

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Upload failed');
                }
                
                const data = await response.json();
                currentText = data.text;
                isFromFile = true;
                originalData.textContent = currentText;
                
                textSection.classList.remove('hidden');
                resetBtn.classList.remove('hidden');
            } catch (error) {
                console.error('Error:', error);
                alert('Error uploading file: ' + error.message);
                resetBtn.classList.add('hidden');
            }
        } else {
            resetBtn.classList.add('hidden');
        }
    });

    // Process button click handler
    processBtn.addEventListener('click', async () => {
        if (!currentText) return;

        try {
            let response;
            if (isFromFile) {
                // Handle file upload case
                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);
                response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Handle sample text case
                response = await fetch('/process_text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: currentText })
                });
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Processing failed');
            }
            
            const data = await response.json();
            showProcessingDescription();
            processedData.textContent = data.processed_data;
            
            processedSection.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Error processing text: ' + error.message);
        }
    });

    // Reset button handler
    resetBtn.addEventListener('click', () => {
        fileInput.value = '';
        currentText = '';
        isFromFile = false;
        
        originalData.innerHTML = '';
        processedData.innerHTML = '';
        
        document.getElementById('process-description').innerHTML = '';
        document.getElementById('process-description').classList.add('hidden');
        
        textSection.classList.add('hidden');
        processedSection.classList.add('hidden');
        
        resetBtn.classList.add('hidden');
        decodedData.innerHTML = '';
        decodedSection.classList.add('hidden');
    });

    // Update sample button handlers
    const sampleBtns = document.querySelectorAll('.sample-btn');
    sampleBtns.forEach(button => {
        button.addEventListener('click', () => {
            const sampleNumber = button.getAttribute('data-sample');
            loadSampleText(sampleNumber);
        });
    });

    async function loadSampleText(sampleNumber) {
        try {
            const response = await fetch(`/sample/${sampleNumber}`);
            if (!response.ok) {
                throw new Error('Failed to load sample text');
            }
            const data = await response.json();
            
            // Clear previous data
            originalData.innerHTML = '';
            processedData.innerHTML = '';
            decodedData.innerHTML = '';  // Clear decoded data
            document.getElementById('process-description').innerHTML = '';
            document.getElementById('process-description').classList.add('hidden');
            processedSection.classList.add('hidden');
            decodedSection.classList.add('hidden');  // Hide decoded section
            
            // Store and display the sample text
            currentText = data.text;
            isFromFile = false;
            originalData.textContent = currentText;
            textSection.classList.remove('hidden');
            resetBtn.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Error loading sample text: ' + error.message);
        }
    }

    // Update decode button handler
    decodeBtn.addEventListener('click', async () => {
        try {
            // Get the processed text and clean it
            const tokenText = processedData.textContent.trim();
            
            const response = await fetch('/decode_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: tokenText })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Decoding failed');
            }
            
            const data = await response.json();
            decodedData.textContent = data.decoded_text;
            decodedSection.classList.remove('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Error decoding text: ' + error.message);
        }
    });
}); 