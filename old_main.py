import pytesseract
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np

def image_processing():
    image_path = 'Image.jpg'
    preprocessed = preprocess_image(image_path)
    if preprocessed is not None:
        visualize_preprocessing(image_path, preprocessed)
    

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Convert to black and white using Otsu's thresholding
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Perform connected component analysis
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
    
    # Create an output image to store the filtered components
    filtered_img = np.zeros_like(bw)
    
    # Filter out small connected components
    min_size = 100  # Minimum size of connected components to keep
    for i in range(1, num_labels):  # Skip the background component
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            filtered_img[labels == i] = 255
    
    return filtered_img

# Use this preprocessed image with Tesseract
preprocessed_img = preprocess_image('Image.jpg')

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
    img = cv2.imread('Image.jpg')
else:
    img = preprocessed_img

# Perform OCR on the image
text = pytesseract.image_to_string(img)

# Print the extracted text
print('The extracted text is:')
print(text)
