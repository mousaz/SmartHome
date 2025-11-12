#!/usr/bin/env python3
"""Ultra-simple image test - just canvas and image, nothing else."""

import tkinter as tk
from PIL import Image, ImageTk
import os

def main():
    print("🎯 Ultra Simple Image Test")
    print("=" * 30)
    
    # Create window
    root = tk.Tk() 
    root.title("Ultra Simple Image Test")
    root.geometry("800x700")
    
    # Create canvas
    canvas = tk.Canvas(root, width=800, height=600, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Load image directly
    image_path = "resources/images/houses/3bedroom001.jpg"
    full_path = os.path.join(os.path.dirname(__file__), image_path)
    
    print(f"📂 Loading: {full_path}")
    print(f"🔍 Exists: {os.path.exists(full_path)}")
    
    if os.path.exists(full_path):
        try:
            image = Image.open(full_path)
            print(f"✅ Opened image: {image.size}")
            
            # Resize to fit nicely
            image.thumbnail((600, 500), Image.Resampling.LANCZOS)
            print(f"📏 Resized to: {image.size}")
            
            photo = ImageTk.PhotoImage(image)
            print(f"🎨 PhotoImage: {photo}")
            
            # Place image in center of canvas
            image_id = canvas.create_image(400, 300, anchor=tk.CENTER, image=photo)
            print(f"🎯 Canvas image ID: {image_id}")
            
            # Add a border around the image to make it obvious
            bbox = canvas.bbox(image_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                border_id = canvas.create_rectangle(x1-5, y1-5, x2+5, y2+5, outline='red', width=3)
                print(f"🔲 Border created: {border_id}")
            
            # Keep reference to prevent garbage collection
            canvas.photo = photo
            
            print("✅ Image should be visible with red border!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            canvas.create_text(400, 300, text=f"Error loading image: {e}", 
                             font=('Arial', 16), fill='red')
    else:
        print("❌ Image file not found")
        canvas.create_text(400, 300, text="Image file not found", 
                         font=('Arial', 16), fill='red')
    
    print("🖥️ Window should now show the image...")
    root.mainloop()

if __name__ == "__main__":
    main()