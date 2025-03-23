from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import ImageTk, Image, ExifTags, ImageSequence
import os
import cv2
import subprocess

# Importing required detection modules
try:
    from ForgeryDetection import Detect
    import double_jpeg_compression
    import noise_variance
    import copy_move_cfa
except ImportError as e:
    print(f"Module Import Error: {e}")

# Global variables
IMG_WIDTH = 400
IMG_HEIGHT = 400
uploaded_image = None
bg_frames = []  # Stores frames of the animated background
bg_index = 0  # Tracks the current frame

def getImage(path, width, height):
    """Returns an image as a PhotoImage object."""
    try:
        img = Image.open(path)
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading image: {e}")
        return None

def browseFile():
    """Open file dialog to select an image."""
    global uploaded_image
    filename = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image Files", "*.jpeg;*.png;*.jpg"), ("All Files", "*.*")]
    )
    
    if not filename:
        return
    
    uploaded_image = filename
    progressBar["value"] = 0  # Reset the progress bar
    fileLabel.config(text=os.path.basename(filename))  # Show only file name
    
    img = getImage(filename, IMG_WIDTH, IMG_HEIGHT)
    if img:
        imagePanel.config(image=img)
        imagePanel.image = img

def copy_move_forgery():
    """Perform copy-move forgery detection."""
    if not uploaded_image:
        messagebox.showerror("Error", "Please select an image")
        return
    
    detect = Detect(uploaded_image)
    
    if hasattr(detect, "siftDetector"):
        detect.siftDetector()
    
    forgery = detect.locateForgery(60, 2)
    progressBar["value"] = 100
    
    if forgery is None:
        resultLabel.config(text="Original Image", foreground="green")
    else:
        resultLabel.config(text="Image Forged", foreground="red")
        cv2.imshow('Forgery', forgery)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def metadata_analysis():
    """Extract metadata from the image."""
    if not uploaded_image:
        messagebox.showerror("Error", "Please select an image")
        return
    
    try:
        img = Image.open(uploaded_image)
        img_exif = img.getexif()
        
        progressBar["value"] = 100
        if not img_exif:
            resultLabel.config(text="No Metadata Found", foreground="red")
        else:
            with open('Metadata_analysis.txt', 'w') as f:
                for key, val in img_exif.items():
                    if key in ExifTags.TAGS:
                        f.write(f"{ExifTags.TAGS[key]}: {val}\n")
            
            subprocess.run(["notepad", "Metadata_analysis.txt"], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Metadata extraction failed: {e}")

def jpeg_Compression():
    """Detect JPEG compression artifacts."""
    if not uploaded_image:
        messagebox.showerror("Error", "Please select an image")
        return
    
    try:
        double_compressed = double_jpeg_compression.detect(uploaded_image)
        progressBar["value"] = 100
        resultLabel.config(
            text="Double Compression" if double_compressed else "Single Compression",
            foreground="red" if double_compressed else "green"
        )
    except AttributeError:
        messagebox.showerror("Error", "JPEG Compression detection function not found.")

def load_animation():
    """Load GIF frames for animation."""
    global bg_frames
    gif_path = "background.gif"  # Replace with the path to your GIF file
    try:
        gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(gif):
            bg_frames.append(ImageTk.PhotoImage(frame))
    except Exception as e:
        print(f"Error loading animation: {e}")

def animate_background():
    """Change background images to create animation effect."""
    global bg_index
    if bg_frames:
        canvas.itemconfig(bg_id, image=bg_frames[bg_index])
        bg_index = (bg_index + 1) % len(bg_frames)
        root.after(100, animate_background)  # Change frame every 100ms

# Initialize GUI
root = Tk()
root.title("Forgery Detection")
root.geometry("800x600")

# Create a Canvas for Animated Background
canvas = Canvas(root, width=500, height=600)
canvas.pack(fill="both", expand=True)

# Load and display the first frame
load_animation()
if bg_frames:
    bg_id = canvas.create_image(0, 0, anchor=NW, image=bg_frames[0])
    animate_background()

# Create Frame for UI Elements
frame = Frame(canvas, padx=10, pady=10, bg="#ffffff", relief=RAISED, borderwidth=2)
frame.place(relx=0.5, rely=0.5, anchor=CENTER)  # Center the frame

fileLabel = Label(frame, text="No file selected", bg="#ffffff", font=("Arial", 10))
fileLabel.pack(pady=5)

imagePanel = Label(frame, bg="#ffffff")
imagePanel.pack(pady=10)

progressBar = ttk.Progressbar(frame, length=300, mode='determinate')
progressBar.pack(pady=5)

browseBtn = Button(frame, text="Browse Image", command=browseFile, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
browseBtn.pack(pady=5)

copyMoveBtn = Button(frame, text="Detect Copy-Move Forgery", command=copy_move_forgery, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
copyMoveBtn.pack(pady=5)

metadataBtn = Button(frame, text="Metadata Analysis", command=metadata_analysis, bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
metadataBtn.pack(pady=5)

jpegBtn = Button(frame, text="JPEG Compression Analysis", command=jpeg_Compression, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
jpegBtn.pack(pady=5)

resultLabel = Label(frame, text="Result will be displayed here", bg="#ffffff", font=("Arial", 10, "bold"))
resultLabel.pack(pady=10)

root.mainloop()
