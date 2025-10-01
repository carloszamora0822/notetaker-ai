let themes = {};
let colorPalette = {};
let currentEditClass = null;
let selectedColor = null;

document.addEventListener('DOMContentLoaded', loadThemes);

async function loadThemes() {
  try {
    const res = await fetch('/api/themes');
    const data = await res.json();
    themes = data.themes;
    colorPalette = data.color_palette;
    
    renderThemeList();
  } catch (error) {
    console.error('Failed to load themes:', error);
  }
}

function renderThemeList() {
  const list = document.getElementById('themeList');
  list.innerHTML = Object.entries(themes)
    .filter(([key]) => key !== 'default')
    .map(([className, theme]) => `
      <div class="theme-card" style="border-left: 4px solid ${theme.primary_color}">
        <div class="theme-info">
          <h3>${className}</h3>
          <div class="color-preview">
            <span class="color-dot" style="background: ${theme.primary_color}"></span>
            <span class="color-name">${theme.color_name || 'custom'}</span>
          </div>
        </div>
        <button onclick="editTheme('${className}')" class="btn-edit">Edit</button>
      </div>
    `).join('');
}

function editTheme(className) {
  currentEditClass = className;
  const theme = themes[className] || themes.default;
  
  document.getElementById('editClassName').textContent = className;
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
  updatePreview(theme.primary_color);
  
  document.getElementById('editModal').classList.remove('hidden');
}

function selectColor(name, primary, secondary) {
  selectedColor = { name, primary, secondary };
  
  // Update active state
  document.querySelectorAll('.color-swatch').forEach(el => {
    el.classList.remove('active');
  });
  event.currentTarget.classList.add('active');
  
  // Update preview
  updatePreview(primary);
}

function updatePreview(color) {
  document.getElementById('previewHeader').style.background = color;
}

async function saveTheme() {
  if (!currentEditClass || !selectedColor) return;
  
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
      closeModal();
      loadThemes();
    }
  } catch (error) {
    alert('Failed to save theme');
  }
}

function addNewClass() {
  const className = prompt('Enter class code (e.g., CS101):');
  if (className) {
    themes[className] = themes.default;
    editTheme(className);
  }
}

function closeModal() {
  document.getElementById('editModal').classList.add('hidden');
  currentEditClass = null;
  selectedColor = null;
}
