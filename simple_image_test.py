#!/usr/bin/env python3
"""
Simple visual test for image loading.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_simple_image_test():
    """Create a simple test window with just the image loading."""
    
    root = tk.Tk()
    root.title("Image Loading Test")
    root.geometry("900x700")
    
    # Create canvas
    canvas = tk.Canvas(root, bg='white', width=800, height=600)
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Load and display image directly
    def load_test_image():
        if not PIL_AVAILABLE:
            canvas.create_text(400, 300, text="PIL not available", font=('Arial', 16))
            return
            
        image_path = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'houses', '3bedroom001.jpg')
        
        if not os.path.exists(image_path):
            canvas.create_text(400, 300, text=f"Image not found:\n{image_path}", font=('Arial', 12))
            return
            
        try:
            # Load image
            with Image.open(image_path) as img:
                print(f"Original image size: {img.size}")
                
                # Resize to fit canvas
                img.thumbnail((700, 500), Image.Resampling.LANCZOS)
                print(f"Resized to: {img.size}")
                
                # Create PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Add to canvas
                image_id = canvas.create_image(400, 300, image=photo)
                print(f"Created image with ID: {image_id}")
                
                # Keep a reference to prevent garbage collection
                canvas.photo = photo
                
                # Add some text over the image
                canvas.create_text(400, 50, text="House Image Loaded Successfully!", 
                                 font=('Arial', 16, 'bold'), fill='red')
                
                return True
                
        except Exception as e:
            canvas.create_text(400, 300, text=f"Error loading image:\n{e}", font=('Arial', 12))
            print(f"Error: {e}")
            return False
    
    # Control buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def clear_canvas():
        canvas.delete("all")
    
    ttk.Button(button_frame, text="Load Image", command=load_test_image).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Clear", command=clear_canvas).pack(side=tk.LEFT, padx=5)
    
    # Status label
    status_label = ttk.Label(button_frame, text="Click 'Load Image' to test")
    status_label.pack(side=tk.RIGHT, padx=5)
    
    # Auto-load on start
    root.after(100, load_test_image)
    
    print("Simple image test window created")
    print("If you see the house image, then PIL and image loading work correctly")
    
    root.mainloop()

if __name__ == '__main__':
    print("Simple Image Loading Test")
    print("=" * 25)
    create_simple_image_test()