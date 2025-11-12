"""
Template loading utilities.
"""

import json
import os


def load_templates():
    """Load templates from JSON file."""
    template_path = os.path.join(os.path.dirname(__file__), 'home_templates.json')
    
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading templates: {e}")
        return {}


def get_template(template_name):
    """Get a specific template by name."""
    templates = load_templates()
    return templates.get(template_name)


def list_templates():
    """List available templates."""
    templates = load_templates()
    return list(templates.keys())


if __name__ == '__main__':
    # Test the template loading
    templates = load_templates()
    print(f"Loaded {len(templates)} templates:")
    
    for key, template in templates.items():
        print(f"  - {key}: {template.get('name', 'No name')}")
        if 'image' in template:
            print(f"    Image: {template['image']}")