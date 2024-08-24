import pytesseract
import cv2
import tkinter as tk
from tkinter import filedialog, scrolledtext, Canvas, Scrollbar, Frame, BOTH
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import sys

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    dilated = cv2.dilate(opening, kernel, iterations=1)
    return dilated

def process_image(image_path):
    global original_image, processed_image
    original_image = cv2.imread(image_path)
    processed_image = preprocess_image(image_path)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(processed_image)
    text_original = pytesseract.image_to_string(original_image)
    text_output.delete('1.0', tk.END)
    text_output.insert(tk.END, "\nOriginal Image Text:\n" + text_original)
    text_output.insert(tk.END, "\n\n---------------------------------\n\n")
    text_output.insert(tk.END, "\nProcessed Image Text:\n" + text)
    display_images()

def resize_image(image, max_size):
    h, w = image.shape[:2]
    if h > w:
        new_h, new_w = max_size, int(w * max_size / h)
    else:
        new_h, new_w = int(h * max_size / w), max_size
    return cv2.resize(image, (new_w, new_h))

def display_images():
    global original_image, processed_image
    max_size = 300
    original_resized = resize_image(original_image, max_size)
    processed_resized = resize_image(processed_image, max_size)

    img = cv2.cvtColor(original_resized, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    original_panel.config(image=img)
    original_panel.image = img

    proc_img = Image.fromarray(processed_resized)
    proc_img = ImageTk.PhotoImage(proc_img)
    processed_panel.config(image=proc_img)
    processed_panel.image = proc_img

def drop(event):
    file_path = event.data
    if file_path.startswith("{") and file_path.endswith("}"):
        file_path = file_path[1:-1]  # Remove curly braces if present
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        process_image(file_path)
    else:
        text_output.delete('1.0', tk.END)
        text_output.insert(tk.END, "Invalid file type. Please drop an image file.")

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.tiff *.bmp")])
    if file_path:
        process_image(file_path)

# Create main window
root = TkinterDnD.Tk()
root.iconbitmap('icon.ico')
root.title("Image OCR Processor")
root.geometry("800x600")

heading = tk.Label(root, text="Image OCR Processor", font=("Arial", 24))
heading.pack(pady=10)

instructions = tk.Label(root, text="Drag and drop an image or use the select button", wraplength=400)
instructions.pack(pady=5)

# Create drag and drop box
drop_box = tk.Label(root, text="Drop Image Here", width=40, height=4, relief="solid")
drop_box.pack(pady=10)
drop_box.drop_target_register(DND_FILES)
drop_box.dnd_bind('<<Drop>>', drop)

# Add select button
select_button = tk.Button(root, text="Select Image", command=select_image, 
                          bg="blue", fg="white", font=("Arial", 12))
select_button.pack(pady=10)

image_frame = tk.Frame(root)
image_frame.pack(pady=10)

original_label = tk.Label(image_frame, text="Original Image")
original_label.pack(side="left", padx=10)

processed_label = tk.Label(image_frame, text="Processed Image")
processed_label.pack(side="right", padx=10)

original_panel = tk.Label(image_frame)
original_panel.pack(side="left", padx=10)

processed_panel = tk.Label(image_frame)
processed_panel.pack(side="right", padx=10)

output_label = tk.Label(root, text="OCR Output:")
output_label.pack(pady=(10,0))

text_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=10)
text_output.pack(pady=10)

root.mainloop()