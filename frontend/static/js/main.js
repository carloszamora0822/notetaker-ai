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

      try {
        const response = await fetch('/rag/query', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ q: query, scope: scope })
        });

        const result = await response.json();

        // Display answer
        const answerDiv = document.querySelector('.answer');
        const answerText = document.getElementById('answerText');
        answerText.textContent = result.answer;
        answerDiv.classList.remove('hidden');

        // Display citations
        const citationsDiv = document.querySelector('.citations');
        const citationList = document.getElementById('citationList');
        citationList.innerHTML = '';

        result.citations.forEach(cite => {
          const li = document.createElement('li');
          li.innerHTML = `<strong>${cite.citation}</strong>: ${cite.chunk.substring(0, 100)}... (score: ${cite.score.toFixed(2)})`;
          citationList.appendChild(li);
        });

        citationsDiv.classList.remove('hidden');
      } catch (error) {
        alert('Search failed: ' + error.message);
      }
    });
  }
});
