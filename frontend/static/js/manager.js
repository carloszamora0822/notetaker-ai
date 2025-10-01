let currentFile = null;

document.addEventListener('DOMContentLoaded', loadFiles);

async function loadFiles() {
  const fileList = document.getElementById('fileList');
  fileList.innerHTML = '<div class="loading">Loading...</div>';
  
  try {
    const res = await fetch('/api/files');
    const data = await res.json();
    
    if (data.files.length === 0) {
      fileList.innerHTML = '<p>No files yet</p>';
      return;
    }
    
    fileList.innerHTML = data.files.map(f => `
      <div class="file-card" onclick="openViewer('${f.filename}')">
        <div class="file-icon">📄</div>
        <div class="file-info">
          <div class="file-name">${f.filename}</div>
          <div class="file-meta">
            <span class="badge">${f.class_code}</span>
            <span>${f.date}</span>
            ${f.has_pdf ? '<span class="pdf-badge">📄 PDF</span>' : ''}
          </div>
        </div>
        <button class="btn-icon" onclick="event.stopPropagation(); deleteFile('${f.filename}')">
          🗑️
        </button>
      </div>
    `).join('');
  } catch (error) {
    fileList.innerHTML = '<p class="error">Failed to load files</p>';
  }
}

async function openViewer(filename) {
  currentFile = filename;
  
  try {
    const res = await fetch(`/api/file/${filename}`);
    const data = await res.json();
    
    document.getElementById('viewerTitle').textContent = filename;
    document.getElementById('fileContent').value = data.content;
    
    // Check if PDF exists
    const pdfBtn = document.getElementById('viewPdfBtn');
    const hasPdf = await checkPDF(filename);
    pdfBtn.classList.toggle('hidden', !hasPdf);
    
    document.getElementById('viewerModal').classList.remove('hidden');
    document.getElementById('pdfViewer').classList.add('hidden');
    document.getElementById('fileContent').classList.remove('hidden');
  } catch (error) {
    alert('Failed to load file');
  }
}

async function checkPDF(filename) {
  const pdfName = filename.replace('.txt', '.pdf');
  try {
    const res = await fetch(`/pdf/${pdfName}`, {method: 'HEAD'});
    return res.ok;
  } catch {
    return false;
  }
}

function viewPDF() {
  if (!currentFile) return;
  const pdfName = currentFile.replace('.txt', '.pdf');
  document.getElementById('pdfViewer').src = `/pdf/${pdfName}`;
  document.getElementById('fileContent').classList.add('hidden');
  document.getElementById('pdfViewer').classList.remove('hidden');
}

async function deleteFile(filename = null) {
  const file = filename || currentFile;
  if (!file || !confirm(`Delete ${file}?`)) return;
  
  try {
    const res = await fetch(`/api/file/${file}`, {method: 'DELETE'});
    const data = await res.json();
    
    if (data.success) {
      alert(`✅ Deleted ${data.deleted_count} items`);
      if (!filename) closeViewer();
      loadFiles();
    }
  } catch (error) {
    alert('Failed to delete');
  }
}

function closeViewer() {
  document.getElementById('viewerModal').classList.add('hidden');
  currentFile = null;
}
