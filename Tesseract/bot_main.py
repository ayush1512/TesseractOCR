import telebot
from telebot import types
import pytesseract
import uuid
import cv2
import os

# Token for the bot
TOKEN = '7479160715:AAH2p9aQUlJ8Zv2f5BdswfvYNUnwUYEUIrw'

# Creating the bot
bot = telebot.TeleBot(TOKEN)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(file_path):
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    dilated = cv2.dilate(opening, kernel, iterations=1)
    return dilated

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        # Get the file ID of the photo
        file_id = message.photo[-1].file_id

        # Get the file path of the photo
        file_path = bot.get_file(file_id).file_path

        # Generate a unique filename for the image
        filename = str(uuid.uuid4()) + '.jpg'

        # Download the photo to your system
        downloaded_file = bot.download_file(file_path)
        with open(filename, 'wb') as f:
            f.write(downloaded_file)

        # Reply to the user
        bot.reply_to(message, 'Image received! Processing...')

        # Preprocess the image
        # preprocessed_img = preprocess_image(filename)

        # Save the preprocessed image
        # preprocessed_filename = 'preprocessed_' + filename
        # cv2.imwrite(preprocessed_filename, preprocessed_img)

        # Perform OCR on the original and preprocessed image
        text_original = pytesseract.image_to_string(filename)
        # text = pytesseract.image_to_string(preprocessed_filename)

        # # Send the preprocessed image back to the user
        # with open(preprocessed_filename, 'rb') as img:
        #     bot.send_photo(message.chat.id, img)

        # Check if the extracted text is empty
        if text_original.strip():
            # Reply with the extracted text
            # bot.reply_to(message, text)
            bot.reply_to(message, text_original)
            print('The extracted text is:', text_original, sep='\n')
        else:
            # Reply with a message indicating that no text was found
            bot.reply_to(message, 'No text found in the image.')
            print('No text found in the image.', sep='\n')

        # Clean up the files
        # os.remove(filename)
        # os.remove(preprocessed_filename)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Start the bot
bot.polling()