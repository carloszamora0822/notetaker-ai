# Frontend Developer Guide

**Your Role**: Jinja2 templates, HTML forms, minimal CSS/JS for UI.

---

## Your Workspace

```bash
cd /path/to/notetaker-ai/frontend
```

**Files you OWN**:
- `frontend/templates/*.html` - Jinja2 templates
- `frontend/static/css/` - Stylesheets
- `frontend/static/js/` - Client-side JavaScript

**Files you READ** (do NOT edit):
- Backend endpoints (via HTTP only)

---

## Sprint 0 Tasks (2-4 hours)

### Task 1: Enhance base template
```html
<!-- frontend/templates/base.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}notetaker-ai{% endblock %}</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <header>
    <h1>📚 notetaker-ai</h1>
    <nav>
      <a href="/">Home</a>
      <a href="/upload">Upload</a>
      <a href="/search">Search</a>
    </nav>
  </header>

  <main>
    {% block content %}{% endblock %}
  </main>

  <footer>
    <p>Offline-first AI note taking</p>
  </footer>

  <script src="/static/js/main.js"></script>
</body>
</html>
```

### Task 2: Create upload form
```html
<!-- frontend/templates/upload.html -->
{% extends "base.html" %}

{% block title %}Upload Notes - notetaker-ai{% endblock %}

{% block content %}
<section class="upload">
  <h2>Upload Class Notes</h2>

  <form id="uploadForm" action="/ingest" method="POST" enctype="multipart/form-data">
    <div class="form-group">
      <label for="file">Select file (.txt, .md, .pdf)</label>
      <input type="file" id="file" name="file" required>
    </div>

    <div class="form-group">
      <label for="class_code">Class Code (optional)</label>
      <input type="text" id="class_code" name="class_code" placeholder="e.g., CS101">
    </div>

    <button type="submit">Upload</button>
  </form>

  <div id="uploadStatus" class="status hidden"></div>
</section>
{% endblock %}
```

### Task 3: Create search/chat interface
```html
<!-- frontend/templates/search.html -->
{% extends "base.html" %}

{% block title %}Search Notes - notetaker-ai{% endblock %}

{% block content %}
<section class="search">
  <h2>Search Your Notes</h2>

  <form id="searchForm">
    <div class="form-group">
      <input type="text" id="query" name="q" placeholder="Ask a question..." required>
      <button type="submit">Search</button>
    </div>

    <div class="form-group">
      <label for="scope">Scope</label>
      <select id="scope" name="scope">
        <option value="all">All Classes</option>
        <option value="current">Current Semester</option>
      </select>
    </div>
  </form>

  <div id="results" class="results">
    <div class="answer hidden">
      <h3>Answer</h3>
      <p id="answerText"></p>
    </div>

    <div class="citations hidden">
      <h3>Sources</h3>
      <ul id="citationList"></ul>
    </div>
  </div>
</section>
{% endblock %}
```

### Task 4: Basic CSS
```css
/* frontend/static/css/main.css */
:root {
  --primary-color: #0B72B9;
  --bg-color: #f5f5f5;
  --text-color: #333;
  --border-color: #ddd;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-color);
  color: var(--text-color);
  line-height: 1.6;
}

header {
  background: var(--primary-color);
  color: white;
  padding: 1rem 2rem;
}

header h1 {
  font-size: 1.5rem;
}

nav {
  margin-top: 0.5rem;
}

nav a {
  color: white;
  text-decoration: none;
  margin-right: 1rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

nav a:hover {
  background: rgba(255,255,255,0.2);
}

main {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

input[type="text"],
input[type="file"],
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

button {
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:hover {
  opacity: 0.9;
}

.hidden {
  display: none;
}

.status {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
}

.status.success {
  background: #d4edda;
  color: #155724;
}

.status.error {
  background: #f8d7da;
  color: #721c24;
}

footer {
  text-align: center;
  padding: 2rem;
  color: #666;
}
```

**Acceptance**:
- [ ] `base.html` renders with navigation
- [ ] Upload form displays and POSTs to `/ingest`
- [ ] Search form displays and POSTs to `/rag/query`
- [ ] Basic CSS applied (no external CDN)

---

## Sprint 1 Tasks (4-8 hours)

### Task 1: Client-side JavaScript for upload
```javascript
// frontend/static/js/main.js

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
```

### Task 2: Class list view
```html
<!-- frontend/templates/classes.html -->
{% extends "base.html" %}

{% block content %}
<section class="classes">
  <h2>Your Classes</h2>

  <div id="classList">
    <!-- Populated by JavaScript -->
  </div>
</section>

<script>
async function loadClasses() {
  const response = await fetch('/api/classes');
  const data = await response.json();

  const container = document.getElementById('classList');
  container.innerHTML = data.classes.map(cls => `
    <div class="class-card">
      <h3>${cls.code}</h3>
      <p>${cls.name || 'No name'}</p>
      <p class="count">${cls.count} notes</p>
    </div>
  `).join('');
}

loadClasses();
</script>
{% endblock %}
```

### Task 3: Responsive design
```css
/* Add to main.css */
@media (max-width: 768px) {
  header {
    padding: 1rem;
  }

  nav {
    display: flex;
    flex-direction: column;
  }

  nav a {
    margin: 0.25rem 0;
  }

  main {
    margin: 1rem auto;
  }
}
```

**Acceptance**:
- [ ] Upload form submits via fetch API, shows status
- [ ] Search displays results without page reload
- [ ] Class list fetches and displays from `/api/classes`
- [ ] Responsive layout works on mobile

---

## Interface Contract (READ-ONLY)

See `docs/API-CONTRACTS.md`. You MUST use ONLY these endpoints:

### HTTP Endpoints (Backend provides):
- `GET /health` - Health check
- `POST /ingest` - Upload document
- `POST /rag/query` - Search notes
- `GET /api/classes` - List classes

**DO NOT** create new endpoints or modify backend code.

---

## Development Loop

```bash
# Backend must be running
make backend

# Edit templates
code frontend/templates/

# Edit CSS/JS
code frontend/static/

# View in browser
open http://localhost:8000

# Before commit
git add -A && git commit -m "feat(frontend): <what you did>"
```

---

## Debugging

### Form not submitting?
- Check browser console for errors (F12)
- Verify backend is running: `curl http://localhost:8000/health`
- Check form action URL matches backend endpoint

### Styles not loading?
- Verify path: `/static/css/main.css`
- Check Backend serves static files (FastAPI mount)

### JavaScript not working?
- Open browser console
- Check for CORS errors
- Verify fetch URLs are correct

---

## Rules (DO NOT VIOLATE)

1. ✅ Use ONLY documented HTTP endpoints from Backend
2. ✅ No external CDNs - fully offline CSS/JS
3. ✅ Handle errors gracefully (show user-friendly messages)
4. ✅ Validate forms client-side before submitting
5. ❌ Do NOT import Backend, RAG, LaTeX, or Ops modules
6. ❌ Do NOT create new API endpoints
7. ❌ Do NOT hardcode URLs - use relative paths

---

## Need Help?

1. Check `docs/API-CONTRACTS.md` for endpoint specs
2. Test endpoints with curl first
3. Check browser console for JavaScript errors
4. Ask Manager (main IDE instance)
