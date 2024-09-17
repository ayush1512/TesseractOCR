import pytesseract
import cv2
import numpy as np
import nltk
import re
from nltk.tokenize import word_tokenize
from datetime import datetime

# Ensure all necessary NLTK data is downloaded
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

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

def perform_ocr(img):
    # Perform OCR on the preprocessed image
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.:-'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text.strip()

def parse_text(text):
    print("Input text:", text)  # Debug print
    
    # First, try parsing with regular expressions
    parsed_info = parse_with_regex(text)
    print("After regex parsing:", parsed_info)  # Debug print
    
    # If regular expression parsing didn't find all fields, try the new method
    if len(parsed_info) < 3:
        parsed_info.update(parse_without_labels(text))
    
    print("Final parsed info:", parsed_info)  # Debug print
    return parsed_info

def parse_with_regex(text):
    # Define regular expressions for each field
    batch_pattern = r'(?:SL|5L|6L|GL|Batch|Lot|B\.?|L\.?)\s*(?:NO|WO)\.?\s*:?\s*([A-Z0-9-]+)'
    mfg_pattern = r'(?:Mfg\.?|Manufacturing\.?|MFD\.?|M\.?|MF\.?|MFOD\.?|MFO\.?)\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    exp_pattern = r'(?:Exp|Expiry|Expiration|EXP|EX)\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    
    # Initialize dictionary to store parsed information
    parsed_info = {}
    
    # Parse the text
    batch_match = re.search(batch_pattern, text, re.IGNORECASE)
    mfg_match = re.search(mfg_pattern, text, re.IGNORECASE)
    exp_match = re.search(exp_pattern, text, re.IGNORECASE)
    
    if batch_match:
        parsed_info['Batch no.'] = batch_match.group(1)
    if mfg_match:
        parsed_info['Mfg date'] = mfg_match.group(1)
    if exp_match:
        parsed_info['Expiry date'] = exp_match.group(1)
    
    return parsed_info

def is_date(string):
    date_patterns = [
        r'\d{1,2}[-/]\d{4}',  # DD-YYYY or MM-YYYY
        r'\d{2}\d{2}\d{2,4}',  # MMDDYYYY or MMDDYY or MMYYYY
        r'\d{2,4}[-/]\d{1,2}',  # YYYY-DD or YYYY-MM
        r'[O0]\d[-/]\d{4}',  # Special case for dates starting with 'O' or '0'
        r'[A-Z]{3}\.?\d{4}'  # MMM.YYYY or MMMYYYY
    ]
    
    print(f"Checking if '{string}' is a date")
    for i, pattern in enumerate(date_patterns):
        if re.match(pattern, string):
            print(f"  Matched date pattern {i+1}: {pattern}")
            return True
    
    print(f"  '{string}' is not recognized as a date")
    return False

def is_price(string):
    price_pattern = r'(?:.*:)?(?:RS\.?)?(?:rs\.?)?(?:Rs\.?)?(\d+(?:\.\d{1,2})?)'
    match = re.match(price_pattern, string, re.IGNORECASE)
    if match:
        try:
            price = float(match.group(1))
            # Round to 2 decimal places
            # price = round(price, 2)
            print(f"'{string}' is recognized as a price: {price}")
            return price
        except ValueError:
            print(f"Error: '{match.group(1)}' could not be converted to a valid price")
            return None
    print(f"'{string}' is not recognized as a price")
    return None

def format_date(date_string):
    print(f"Formatting date: {date_string}")
    if date_string.startswith('O'):
        date_string = '0' + date_string[1:]
    
    for fmt in ('%b.%Y', '%b%Y', '%m%Y', '%m-%Y', '%d-%Y', '%Y-%m', '%Y-%d', '%m/%Y', '%d/%Y', '%Y/%m', '%Y/%d', '%m%d%Y', '%d%m%Y', '%Y%m%d', '%Y%d%m'):
        try:
            date = datetime.strptime(date_string, fmt)
            formatted_date = date.strftime('%m/%Y')
            print(f"Formatted date: {formatted_date}")
            return formatted_date
        except ValueError:
            continue
    
    print(f"No format matched, returning original: {date_string}")
    return date_string

def parse_without_labels(text):
    print("Parsing without labels")
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print("Lines:", lines)

    parsed_info = {}
    prices = []

    for i, line in enumerate(lines):
        print(f"\nProcessing line {i}: {line}")
        if i == 0 and 'Batch no.' not in parsed_info:
            parsed_info['Batch no.'] = line.lstrip('-')
            print(f"Batch no. set to: {parsed_info['Batch no.']}")
        elif is_date(line):
            if 'Mfg date' not in parsed_info:
                parsed_info['Mfg date'] = format_date(line)
                print(f"Mfg date set to: {parsed_info['Mfg date']}")
            elif 'Expiry date' not in parsed_info:
                parsed_info['Expiry date'] = format_date(line)
                print(f"Expiry date set to: {parsed_info['Expiry date']}")
        else:
            price = is_price(line)
            if price is not None:
                prices.append(price)
            else:
                print(f"Line {i} is not recognized as a date or price")

    if len(prices) >= 2:
        parsed_info['MRP'] = max(prices)
        parsed_info['Price per item'] = min(prices)
    elif len(prices) == 1:
        parsed_info['MRP'] = prices[0]

    return parsed_info

def main():
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Preprocess the image
    image_path = 'Image.jpg'
    preprocessed_img = preprocess_image(image_path)
    
    # Perform OCR
    extracted_text = perform_ocr(preprocessed_img)
    
    print('The extracted text is:')
    print(extracted_text)
    
    # Parse the extracted text
    parsed_info = parse_text(extracted_text)
    
    print('\nParsed Information:')
    for key, value in parsed_info.items():
        print(f'{key}: {value}')

if __name__ == "__main__":
    main()