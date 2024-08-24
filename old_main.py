import pytesseract
import cv2
import os
import matplotlib.pyplot as plt

def image_processing():
    image_path = 'WhatsApp Image 2024-08-14 at 21.11.05_c0e2ecd9.jpg'
    preprocessed = preprocess_image(image_path)
    if preprocessed is not None:
        visualize_preprocessing(image_path, preprocessed)
    

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Perform morphological operations to remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Dilate to connect nearby text components
    dilated = cv2.dilate(opening, kernel, iterations=1)
    
    return dilated

# Use this preprocessed image with Tesseract
preprocessed_img = preprocess_image('WhatsApp Image 2024-08-14 at 21.11.05_c0e2ecd9.jpg')

def visualize_preprocessing(original_path, preprocessed_img):
    original = cv2.imread(original_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(12, 6))
    plt.subplot(121), plt.imshow(original_rgb), plt.title('Original')
    plt.subplot(122), plt.imshow(preprocessed_img, cmap='gray'), plt.title('Preprocessed')
    plt.show()

    # Save the preprocessed image
    cv2.imwrite('preprocessed_image.jpg', preprocessed_img)
    # Delete the image file
    os.remove('preprocessed_image.jpg')
    
image_processing()

# Then pass preprocessed_img to Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Open an image file
if(preprocessed_img is None):
    img = cv2.imread('WhatsApp Image 2024-08-14 at 21.11.05_c0e2ecd9.jpg')
else:
    img = preprocessed_img

# Perform OCR on the image
text = pytesseract.image_to_string(img)

# Print the extracted text
print('The extracted text is:')
print(text)
