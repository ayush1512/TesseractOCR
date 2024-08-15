import pytesseract
import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    dilated = cv2.dilate(opening, kernel, iterations=1)
    return dilated

def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global original_image, processed_image
        original_image = cv2.imread(file_path)
        processed_image = preprocess_image(file_path)
        display_images()
        process_image()

def display_images():
    # Display original image
    img = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    original_panel.config(image=img)
    original_panel.image = img

    # Display processed image
    proc_img = Image.fromarray(processed_image)
    proc_img = ImageTk.PhotoImage(proc_img)
    processed_panel.config(image=proc_img)
    processed_panel.image = proc_img

def process_image():
    global processed_image
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(processed_image)
    text_output.delete('1.0', tk.END)
    text_output.insert(tk.END, text)

def resize_image(image, max_size):
    h, w = image.shape[:2]
    if h > w:
        new_h, new_w = max_size, int(w * max_size / h)
    else:
        new_h, new_w = int(h * max_size / w), max_size
    return cv2.resize(image, (new_w, new_h))

def display_images():
    global original_image, processed_image
    
    # Resize images
    max_size = 300  # Maximum width or height in pixels
    original_resized = resize_image(original_image, max_size)
    processed_resized = resize_image(processed_image, max_size)

    # Display original image
    img = cv2.cvtColor(original_resized, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    original_panel.config(image=img)
    original_panel.image = img

    # Display processed image
    proc_img = Image.fromarray(processed_resized)
    proc_img = ImageTk.PhotoImage(proc_img)
    processed_panel.config(image=proc_img)
    processed_panel.image = proc_img
    
# Create main window
root = tk.Tk()
root.title("Image OCR Processor")
root.geometry("800x600")

heading = tk.Label(root, text="Image OCR Processor", font=("Arial", 24))
heading.pack(pady=10)

instructions = tk.Label(root, text="Select an image to process. The OCR result will appear below.", wraplength=400)
instructions.pack(pady=5)

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