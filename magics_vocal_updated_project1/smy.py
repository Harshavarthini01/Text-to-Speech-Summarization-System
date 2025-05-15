import os
import nltk
import pytesseract
from pdf2image import convert_from_path
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import pyttsx3
import PyPDF2
from tkinter import Tk
from tkinter.filedialog import askopenfilename

nltk.download('punkt')
nltk.download('stopwords')

# Path to Poppler if on Windows
POPPLER_PATH = r"C:\poppler\Library\bin"  # <- change if installed somewhere else

# Extract text from scanned or text-based PDFs
def extract_text_from_file(file_path):
    text = ''
    if file_path.endswith(".txt"):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith(".pdf"):
        try:
            # Try reading text-based PDF
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except:
            pass

        # If still no text, try OCR on scanned images
        if not text.strip():
            print("[INFO] No text found with PyPDF2. Using OCR...")
            images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
            for img in images:
                text += pytesseract.image_to_string(img)

        return text
    else:
        raise ValueError("Unsupported file format. Please use .txt or .pdf")

# Frequency summarizer
def frequency_summary(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)

    freq_table = {}
    for word in words:
        word = word.lower()
        if word in stop_words:
            continue
        freq_table[word] = freq_table.get(word, 0) + 1

    sentences = sent_tokenize(text)
    sentence_value = {}
    for sentence in sentences:
        for word, freq in freq_table.items():
            if word in sentence.lower():
                sentence_value[sentence] = sentence_value.get(sentence, 0) + freq

    average = int(sum(sentence_value.values()) / len(sentence_value)) if sentence_value else 0
    summary = ''
    for sentence in sentences:
        if sentence in sentence_value and sentence_value[sentence] > (1.2 * average):
            summary += sentence + " "
    return summary.strip()

# Speak text aloud
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print("\nAvailable Voices:")
    for index, voice in enumerate(voices):
        print(f"{index}: {voice.name} ({voice.id})")

    try:
        selected_voice_index = int(input("\nEnter the number of the voice you want to use: "))
        engine.setProperty('voice', voices[selected_voice_index].id)
    except (ValueError, IndexError):
        print("Invalid input. Using default voice.")

    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# Main
def summarize_file():
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")])
    if not file_path:
        print("No file selected.")
        return

    print("[INFO] Extracting text...")
    text = extract_text_from_file(file_path)

    print("\n[Summary]:")
    freq_summary = frequency_summary(text)
    print(freq_summary)

    print("\n[Text-to-Speech Output]:")
    speak(freq_summary)

if __name__ == "__main__":
    summarize_file()
