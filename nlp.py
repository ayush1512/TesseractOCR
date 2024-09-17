import pytesseract
import cv2
import numpy as np
import nltk
import re
from nltk.tokenize import word_tokenize
from datetime import datetime

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
    filtered_img = np.zeros_like(bw)
    min_size = 100
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            filtered_img[labels == i] = 255
    return filtered_img

def perform_ocr(img):
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.:-'
    text = pytesseract.image_to_string(img, config=custom_config)
    return text.strip()

def parse_text(text):
    parsed_info = parse_with_regex(text)
    if len(parsed_info) < 3:
        parsed_info.update(parse_without_labels(text))
    return parsed_info

def parse_with_regex(text):
    batch_pattern = r'(?:SL|5L|6L|GL|Batch|Lot|B\.?|L\.?)\s*(?:NO|WO)\.?\s*:?\s*([A-Z0-9-]+)'
    mfg_pattern = r'(?:Mfg\.?|Manufacturing\.?|MFD\.?|M\.?|MF\.?|MFOD\.?|MFO\.?)\s*([A-Z]{3,4}\.?\s*\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    exp_pattern = r'(?:Exp|Expiry|Expiration|EXP|EX)\s*:?\s*([A-Z]{3,4}\.?\s*\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    
    parsed_info = {}
    
    batch_match = re.search(batch_pattern, text, re.IGNORECASE)
    mfg_match = re.search(mfg_pattern, text, re.IGNORECASE)
    exp_match = re.search(exp_pattern, text, re.IGNORECASE)
    
    if batch_match:
        parsed_info['Batch no.'] = batch_match.group(1)
    if mfg_match:
        parsed_info['Mfg date'] = format_date(mfg_match.group(1))
    if exp_match:
        parsed_info['Expiry date'] = format_date(exp_match.group(1))
    
    return parsed_info

def is_date(string):
    date_patterns = [
        r'\d{1,2}[-/]\d{4}',
        r'\d{2}\d{2}\d{2,4}',
        r'\d{2,4}[-/]\d{1,2}',
        r'[O0]\d[-/]\d{4}',
        r'[A-Z]{3,4}\.?\s*\d{4}'
    ]
    
    return any(re.match(pattern, string) for pattern in date_patterns)

def is_price(string):
    price_pattern = r'(?:.*:)?(?:RS\.?)?(?:rs\.?)?(?:Rs\.?)?(\d+(?:\.\d{1,2})?)'
    match = re.match(price_pattern, string, re.IGNORECASE)
    if match:
        try:
            price = float(match.group(1))
            return "{:.2f}".format(price)  # Format price to always have 2 decimal places
        except ValueError:
            return None
    return None

def format_date(date_string):
    months = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
        'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }
    
    # Check if the date is in the format "MMM.YYYY" or "MMMYYYY"
    match = re.match(r'([A-Z]{3,4})\.?\s*(\d{4})', date_string.upper())
    if match:
        month, year = match.groups()
        if month in months:
            return f"{months[month]}/{year}"
    
    # If not, try parsing with datetime
    for fmt in ('%m%Y', '%m-%Y', '%d-%Y', '%Y-%m', '%Y-%d', '%m/%Y', '%d/%Y', '%Y/%m', '%Y/%d', '%m%d%Y', '%d%m%Y', '%Y%m%d', '%Y%d%m'):
        try:
            date = datetime.strptime(date_string, fmt)
            return date.strftime('%m/%Y')
        except ValueError:
            continue
    
    return date_string  # Return original if parsing fails

def parse_without_labels(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    parsed_info = {}
    prices = []

    for i, line in enumerate(lines):
        if i == 0 and 'Batch no.' not in parsed_info:
            parsed_info['Batch no.'] = line.lstrip('-')
        elif is_date(line):
            if 'Mfg date' not in parsed_info:
                parsed_info['Mfg date'] = format_date(line)
            elif 'Expiry date' not in parsed_info:
                parsed_info['Expiry date'] = format_date(line)
        else:
            price = is_price(line)
            if price is not None:
                prices.append(price)

    if len(prices) >= 2:
        parsed_info['MRP'] = max(prices)
        parsed_info['Price per item'] = min(prices)
    elif len(prices) == 1:
        parsed_info['MRP'] = prices[0]

    return parsed_info

def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    image_path = 'Image.jpg'
    preprocessed_img = preprocess_image(image_path)
    
    extracted_text = perform_ocr(preprocessed_img)
    
    parsed_info = parse_text(extracted_text)
    
    print('\nParsed Information:')
    for key, value in parsed_info.items():
        print(f'{key}: {value}')

if __name__ == "__main__":
    main()