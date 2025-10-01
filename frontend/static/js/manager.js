let currentFile = null;
let themes = {};
let colorPalette = {};
let currentEditClass = null;
let selectedColor = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadThemes();
  await loadFiles();
});

async function loadThemes() {
  try {
    const res = await fetch('/api/themes');
    const data = await res.json();
    themes = data.themes;
    colorPalette = data.color_palette;
  } catch (error) {
    console.error('Failed to load themes:', error);
  }
}

async function loadFiles() {
  const fileList = document.getElementById('fileList');
  fileList.innerHTML = '<div class="loading">Loading files...</div>';
  
  try {
    const res = await fetch('/api/files');
    const data = await res.json();
    
    if (data.files.length === 0) {
      fileList.innerHTML = '<p class="empty">No files yet</p>';
      return;
    }
    
    // Group files by class
    const filesByClass = {};
    data.files.forEach(f => {
      if (!filesByClass[f.class_code]) {
        filesByClass[f.class_code] = [];
      }
      filesByClass[f.class_code].push(f);
    });
    
    // Render class sections
    fileList.innerHTML = Object.entries(filesByClass).map(([className, files]) => {
      const theme = themes[className] || themes.default || {};
      const color = theme.primary_color || '#0B72B9';
      
      return `
        <div class="class-section">
          <div class="class-header" style="border-left: 4px solid ${color}">
            <div class="class-title">
              <span class="class-dot" style="background: ${color}"></span>
              <h2>${className}</h2>
              <span class="file-count">${files.length} file${files.length !== 1 ? 's' : ''}</span>
            </div>
            <button class="btn-edit-theme" onclick="editTheme('${className}')" title="Edit Theme">
              Edit Theme
            </button>
          </div>
          <div class="class-files">
            ${files.map(f => `
              <div class="file-card" onclick="openViewer('${f.filename}')">
                <div class="file-icon">📄</div>
                <div class="file-info">
                  <div class="file-name">${f.filename}</div>
                  <div class="file-meta">
                    <span>${f.date}</span>
                  </div>
                </div>
                <div class="file-actions">
                  ${f.has_pdf ? `<button class="btn-pdf" onclick="event.stopPropagation(); window.open('${f.pdf_url}', '_blank')" title="View PDF">📄 PDF</button>` : ''}
                  <button class="btn-icon" onclick="event.stopPropagation(); deleteFile('${f.filename}')" title="Delete">
                    🗑️
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }).join('');
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
    
    document.getElementById('viewerModal').classList.remove('hidden');
  } catch (error) {
    alert('Failed to load file');
  }
}

function editTheme(className) {
  currentEditClass = className;
  const theme = themes[className] || themes.default || {};
  
  document.getElementById('themeClassName').textContent = className;
  document.getElementById('previewClassName').textContent = className;
  
  // Render color swatches
  const swatches = document.getElementById('colorSwatches');
  swatches.innerHTML = Object.entries(colorPalette).map(([name, colors]) => `
    <div class="color-swatch ${theme.color_name === name ? 'active' : ''}" 
         onclick="selectColor('${name}', '${colors.primary}', '${colors.secondary}')">
      <div class="swatch-color" style="background: ${colors.primary}"></div>
      <span>${name}</span>
    </div>
  `).join('');
  
  // Update preview
  updateThemePreview(theme.primary_color || '#0B72B9');
  
  document.getElementById('themeModal').classList.remove('hidden');
}

function selectColor(name, primary, secondary) {
  selectedColor = { name, primary, secondary };
  
  // Update active state
  document.querySelectorAll('.color-swatch').forEach(el => {
    el.classList.remove('active');
  });
  event.currentTarget.classList.add('active');
  
  // Update preview
  updateThemePreview(primary);
}

function updateThemePreview(color) {
  document.getElementById('themePreview').style.background = color;
}

async function saveTheme() {
  if (!currentEditClass || !selectedColor) {
    alert('Please select a color');
    return;
  }
  
  const theme = {
    color_name: selectedColor.name,
    primary_color: selectedColor.primary,
    secondary_color: selectedColor.secondary
  };
  
  try {
    const res = await fetch(`/api/themes/${currentEditClass}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(theme)
    });
    
    if (res.ok) {
      alert('✅ Theme saved!');
      closeThemeEditor();
      // Reload themes and files
      await loadThemes();
      await loadFiles();
    }
  } catch (error) {
    alert('Failed to save theme');
  }
}

function closeThemeEditor() {
  document.getElementById('themeModal').classList.add('hidden');
  currentEditClass = null;
  selectedColor = null;
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

// Class Management Functions
async function openClassManager() {
  try {
    const res = await fetch('/api/classes');
    const data = await res.json();
    
    const list = document.getElementById('classList');
    list.innerHTML = data.classes.map(cls => `
      <div class="class-manage-card">
        <div class="class-info">
          <span class="class-dot" style="background: ${cls.color || '#0B72B9'}"></span>
          <strong>${cls.code}</strong>
          <span class="file-count">${cls.file_count} files</span>
        </div>
        <div class="class-actions">
          <button onclick="editTheme('${cls.code}')" class="btn-edit">🎨 Theme</button>
          ${cls.file_count === 0 ? 
            `<button onclick="deleteClass('${cls.code}')" class="btn-danger">🗑️ Delete</button>`  
            : ''}
        </div>
      </div>
    `).join('');
    
    document.getElementById('classManagerModal').classList.remove('hidden');
  } catch (error) {
    alert('Failed to load classes');
  }
}

async function deleteClass(className) {
  if (!confirm(`Delete class "${className}"? This cannot be undone.`)) return;
  
  try {
    const res = await fetch(`/api/classes/${className}`, { method: 'DELETE' });
    if (res.ok) {
      alert(`✅ Deleted ${className}`);
      openClassManager(); // Refresh
      loadFiles(); // Refresh main view
    } else {
      const error = await res.json();
      alert(`Error: ${error.detail}`);
    }
  } catch (error) {
    alert('Failed to delete class');
  }
}

function closeClassManager() {
  document.getElementById('classManagerModal').classList.add('hidden');
}
