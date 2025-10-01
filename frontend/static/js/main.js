// Simple markdown to HTML converter
function markdownToHtml(text) {
  return text
    // Headers
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Bullet points (• or -)
    .replace(/^[•\-] (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/(<li>.*<\/li>\n?)+/gs, '<ul>$&</ul>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    // Wrap in paragraph
    .replace(/^(.+)$/gm, function(match) {
      if (match.startsWith('<h') || match.startsWith('<ul') || match.startsWith('<li>')) {
        return match;
      }
      return match;
    });
}

document.addEventListener('DOMContentLoaded', () => {
  // Upload form handler
  const uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    // Load classes for dropdown
    loadClassesForUpload();
    
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData();
      const file = document.getElementById('file').files[0];
      
      // Use new class input if filled, otherwise use dropdown
      let classCode = document.getElementById('new_class_code').value.trim();
      if (!classCode) {
        classCode = document.getElementById('class_code').value;
      }
      
      formData.append('file', file);
      formData.append('class_code', classCode);
      
      const statusDiv = document.getElementById('uploadStatus');

      statusDiv.className = 'status';
      statusDiv.textContent = 'Uploading...';
      statusDiv.classList.remove('hidden');

      try {
        const response = await fetch('/ingest', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();

        if (response.ok) {
          statusDiv.className = 'status success';
          statusDiv.textContent = `✓ Uploaded successfully! Stored at: ${result.stored}`;
          uploadForm.reset();
          // Hide new class input after successful upload
          document.getElementById('new_class_code').classList.add('hidden');
          // Reload classes
          loadClassesForUpload();
        } else {
          throw new Error('Upload failed');
        }
      } catch (error) {
        statusDiv.className = 'status error';
        statusDiv.textContent = `✗ Error: ${error.message}`;
      }
    });
  }

  // Search form handler
  const searchForm = document.getElementById('searchForm');
  if (searchForm) {
    // Load class list for scope dropdown
    loadClassesForSearch();
    
    searchForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const query = document.getElementById('query').value;
      const scope = document.getElementById('scope').value;
      const resultsDiv = document.getElementById('results');

      // Show loading state
      resultsDiv.innerHTML = `
        <div class="loading">
          <div class="spinner"></div>
          <p>🤔 Thinking and analyzing your notes...</p>
        </div>
      `;

      try {
        const response = await fetch('/rag/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ q: query, scope: scope })
        });

        const data = await response.json();

        // Show synthesized answer
        const formattedAnswer = markdownToHtml(data.answer);
        resultsDiv.innerHTML = `
          <div class="answer">
            <h3>Answer ${data.synthesized ? '<span class="badge">✨ AI-Enhanced</span>' : ''}</h3>
            <div class="answer-content">${formattedAnswer}</div>
          </div>
          <div class="sources">
            <h3>Sources (${data.num_sources || data.citations.length})</h3>
            ${data.citations.map(c => `
              <div class="source">
                <strong>${c.citation}</strong>: ${c.chunk.substring(0, 150)}...
              </div>
            `).join('')}
          </div>
        `;

      } catch (error) {
        resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
      }
    });
  }
});

// Load classes into search scope dropdown
async function loadClassesForSearch() {
  const scopeSelect = document.getElementById('scope');
  if (!scopeSelect) return;
  
  try {
    const response = await fetch('/api/files');
    const data = await response.json();
    
    // Get unique class codes
    const classes = [...new Set(data.files.map(f => f.class_code))];
    
    // Add class options
    classes.forEach(className => {
      const option = document.createElement('option');
      option.value = className.toLowerCase();
      option.textContent = className;
      scopeSelect.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load classes:', error);
  }
}

// Load classes into upload dropdown
async function loadClassesForUpload() {
  const select = document.getElementById('class_code');
  if (!select) return;
  
  try {
    const res = await fetch('/api/classes');
    const data = await res.json();
    
    // Clear existing options except first one
    select.innerHTML = '<option value="">Select class...</option>';
    
    data.classes.forEach(cls => {
      const option = document.createElement('option');
      option.value = cls.code;
      option.textContent = `${cls.code} (${cls.file_count} files)`;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load classes:', error);
  }
}

// Toggle new class input
function showNewClassInput() {
  const select = document.getElementById('class_code');
  const newInput = document.getElementById('new_class_code');
  
  if (newInput.classList.contains('hidden')) {
    newInput.classList.remove('hidden');
    newInput.focus();
    select.value = '';
  } else {
    newInput.classList.add('hidden');
    newInput.value = '';
  }
}
