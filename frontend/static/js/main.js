document.addEventListener('DOMContentLoaded', () => {
  // Upload form handler
  const uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const formData = new FormData(uploadForm);
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
        resultsDiv.innerHTML = `
          <div class="answer">
            <h3>Answer</h3>
            <p>${data.answer}</p>
            ${data.synthesized ? '<span class="badge">✨ AI-Enhanced</span>' : ''}
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
