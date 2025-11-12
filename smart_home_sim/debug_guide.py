"""
Debug Guide for Smart Home Application
=====================================

This file contains guidance for debugging the Smart Home application,
particularly focusing on the image loading functionality.

Key Places to Set Breakpoints:
==============================

1. Template Loading:
   - src/gui/home_view.py:load_template() - line ~725
   - Set breakpoint here to see when templates are loaded

2. Image Drawing:
   - src/gui/home_view.py:draw_background_image() - line ~378
   - Set breakpoint here to debug image loading process

3. Canvas Sizing:
   - src/gui/home_view.py:update_background_image_size() - line ~467
   - Set breakpoint here to debug canvas resizing issues

4. Template Layout:
   - src/gui/home_view.py:draw_template_layout() - line ~332
   - Set breakpoint here to see template processing

5. Canvas Events:
   - src/gui/home_view.py:on_canvas_resize() - line ~520
   - Set breakpoint here to debug resize events

Debug Workflow:
==============
1. Open VS Code in the smart_home_sim folder
2. Set breakpoints at the locations mentioned above
3. Use "Debug Smart Home App" configuration
4. Load a template (Family House or Studio Apartment)
5. Step through the code to see:
   - Template data loading
   - Image path resolution
   - PIL image loading
   - PhotoImage creation
   - Canvas positioning

Common Issues to Check:
======================
- Check self.background_image is loaded correctly
- Check self.background_photo is created
- Check self.background_image_id is set
- Check canvas dimensions (canvas_width, canvas_height)
- Check image positioning (center_x, center_y)
- Check show_background variable state

Variables to Watch:
==================
- self.home_template
- self.background_image
- self.background_photo 
- self.background_image_id
- canvas_width, canvas_height
- center_x, center_y
- image_loaded (return value)
"""

def debug_image_loading_tips():
    """Print debugging tips for image loading."""
    print("🔍 Image Loading Debug Tips:")
    print("=" * 40)
    print("1. Set breakpoint in draw_background_image()")
    print("2. Check if PIL_AVAILABLE is True")
    print("3. Verify template has 'image' key")
    print("4. Check full_image_path exists")
    print("5. Verify PIL Image.open() succeeds")
    print("6. Check canvas dimensions are > 1")
    print("7. Verify PhotoImage creation")
    print("8. Check canvas.create_image() returns valid ID")
    print("9. Verify show_background.get() is True")

if __name__ == "__main__":
    debug_image_loading_tips()