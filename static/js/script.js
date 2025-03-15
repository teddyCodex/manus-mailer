// JavaScript for the Bulk Email Sender application

document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for file input to show selected file names
    const fileInput = document.getElementById('files');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileCount = this.files.length;
            let fileNames = '';
            
            if (fileCount > 0) {
                fileNames = `Selected ${fileCount} file(s): `;
                for (let i = 0; i < fileCount; i++) {
                    fileNames += this.files[i].name;
                    if (i < fileCount - 1) {
                        fileNames += ', ';
                    }
                }
            }
            
            // Create or update file list display
            let fileListDisplay = document.getElementById('file-list-display');
            if (!fileListDisplay) {
                fileListDisplay = document.createElement('div');
                fileListDisplay.id = 'file-list-display';
                fileListDisplay.className = 'form-text mt-2';
                this.parentNode.appendChild(fileListDisplay);
            }
            
            fileListDisplay.textContent = fileNames;
        });
    }
    
    // Add event listeners for placeholder insertion buttons in compose page
    const contentTextarea = document.getElementById('content');
    const subjectInput = document.getElementById('subject');
    
    if (contentTextarea && subjectInput) {
        // Create placeholder buttons
        const placeholderContainer = document.createElement('div');
        placeholderContainer.className = 'mb-3 mt-2';
        placeholderContainer.innerHTML = `
            <label class="form-label">Insert placeholder:</label>
            <button type="button" class="btn btn-sm btn-outline-secondary me-2" data-placeholder="{{name}}">Name</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-placeholder="{{email}}">Email</button>
        `;
        
        // Insert after subject input
        subjectInput.parentNode.appendChild(placeholderContainer);
        
        // Add event listeners to buttons
        const buttons = placeholderContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                const placeholder = this.getAttribute('data-placeholder');
                const activeElement = document.activeElement;
                
                if (activeElement === subjectInput || activeElement === contentTextarea) {
                    // Insert at cursor position
                    const start = activeElement.selectionStart;
                    const end = activeElement.selectionEnd;
                    const value = activeElement.value;
                    
                    activeElement.value = value.substring(0, start) + placeholder + value.substring(end);
                    
                    // Set cursor position after inserted placeholder
                    activeElement.selectionStart = activeElement.selectionEnd = start + placeholder.length;
                    activeElement.focus();
                } else {
                    // Default to content textarea if no element is focused
                    contentTextarea.value += placeholder;
                    contentTextarea.focus();
                }
            });
        });
    }
});
