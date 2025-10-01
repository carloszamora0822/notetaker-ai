"""Unified class registry and theme management"""
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime

THEMES_FILE = Path(__file__).parent / "class_themes.yaml"


def load_themes() -> Dict:
    """Load all class themes (single source of truth)"""
    if not THEMES_FILE.exists():
        return create_default_config()
    
    with open(THEMES_FILE) as f:
        return yaml.safe_load(f)


def create_default_config() -> Dict:
    """Create default config if none exists"""
    default = {
        "default": {
            "color_name": "blue",
            "primary_color": "#0B72B9",
            "secondary_color": "#64B5F6",
            "file_count": 0,
            "created_at": datetime.now().isoformat()
        },
        "color_palette": {
            "blue": {"primary": "#0B72B9", "secondary": "#64B5F6"},
            "green": {"primary": "#28a745", "secondary": "#66bb6a"},
            "red": {"primary": "#dc3545", "secondary": "#ff6b6b"},
            "orange": {"primary": "#fd7e14", "secondary": "#ffa94d"},
            "yellow": {"primary": "#ffc107", "secondary": "#ffd43b"},
            "purple": {"primary": "#764ba2", "secondary": "#9c27b0"}
        }
    }
    save_themes(default)
    return default


def list_all_classes() -> List[str]:
    """Get list of all registered classes"""
    themes = load_themes()
    return [k for k in themes.keys() if k not in ['default', 'color_palette']]


def get_theme(class_code: str) -> Dict:
    """Get theme for specific class, fallback to default"""
    themes = load_themes()
    return themes.get(class_code, themes.get("default", {}))


def class_exists(class_code: str) -> bool:
    """Check if class is registered"""
    themes = load_themes()
    return class_code in themes and class_code not in ['default', 'color_palette']


def register_class(class_code: str, color: str = None) -> Dict:
    """Register new class with default or specified color"""
    themes = load_themes()
    
    if class_exists(class_code):
        return themes[class_code]
    
    # Auto-assign color from palette if not specified
    if not color:
        palette = themes.get('color_palette', {})
        used_colors = set(t.get('color_name') for t in themes.values() if isinstance(t, dict))
        available = [c for c in palette.keys() if c not in used_colors]
        color = available[0] if available else 'blue'
    
    palette = themes.get('color_palette', {})
    theme = {
        "color_name": color,
        "primary_color": palette.get(color, {}).get('primary', '#0B72B9'),
        "secondary_color": palette.get(color, {}).get('secondary', '#64B5F6'),
        "file_count": 0,
        "created_at": datetime.now().isoformat()
    }
    
    themes[class_code] = theme
    save_themes(themes)
    return theme


def increment_file_count(class_code: str):
    """Increment file count for class"""
    themes = load_themes()
    if class_code in themes:
        themes[class_code]['file_count'] = themes[class_code].get('file_count', 0) + 1
        save_themes(themes)


def decrement_file_count(class_code: str):
    """Decrement file count for class"""
    themes = load_themes()
    if class_code in themes:
        themes[class_code]['file_count'] = max(0, themes[class_code].get('file_count', 0) - 1)
        save_themes(themes)


def save_themes(themes: Dict):
    """Save themes to file"""
    with open(THEMES_FILE, 'w') as f:
        yaml.dump(themes, f, default_flow_style=False, sort_keys=False)


def save_theme(class_code: str, theme: Dict):
    """Save or update a class theme"""
    themes = load_themes()
    themes[class_code] = theme
    save_themes(themes)


def delete_class(class_code: str):
    """Delete class from registry"""
    themes = load_themes()
    if class_code in themes and class_code not in ['default', 'color_palette']:
        del themes[class_code]
        save_themes(themes)


def delete_theme(class_code: str):
    """Delete a class theme (revert to default)"""
    delete_class(class_code)


def get_color_palette() -> Dict:
    """Get available color options"""
    themes = load_themes()
    return themes.get("color_palette", {})
