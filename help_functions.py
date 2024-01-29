import pytesseract
import pdfplumber
import spacy
from fuzzywuzzy import fuzz
from google.cloud import vision
from google.oauth2 import service_account
import io
from pdf2image import convert_from_bytes, convert_from_path

### Extract all the information from pdf to text
def extract_text_from_image_pdf(pdf_path, res):
    """
    pdf_path: path to the pdf file
    res: resolution of the image to get the text
    """
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)

        for page_number in range(1, num_pages + 1):
            # Extract the image from the PDF page
            page = pdf.pages[page_number - 1]
            image = page.to_image(resolution=res)  # You can adjust the resolution as needed

            # Convert the image to text using Tesseract
            text = pytesseract.image_to_string(image.original, lang='spa')
            name_file = f'{pdf_path[:-4]}_page_{page_number}.txt'
            print(name_file)
            with open(name_file, 'w') as the_file:
                the_file.write(text)
            # Print or process the extracted text as needed
            #print(f"Page {page_number}:\n{text}\n{'='*50}\n")
                
### Extract the information from pdf to text in a particular page
def extract_text_from_image_pdf_page(pdf_path, page_number, res):
    """
    pdf_path: path to the pdf file
    page_numer: number of the page to extract the data from the pdf
    res: resolution of the image to get the text
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Extract the image from the PDF page
        page = pdf.pages[page_number - 1]
        image = page.to_image(resolution=res)  # You can adjust the resolution as needed

        # Convert the image to text using Tesseract
        text = pytesseract.image_to_string(image.original, lang='eng')
        #text = text.lower()
        return text

# Extract the information required
def extract_info(text, string1,threshold):
    """
    text: text to be processed
    string1: String to replace strings with errors in text
    threshold: Threshold to measure the similarity between string1 and the strings with errors
               in text
    """
    nlp = spacy.load("es_core_news_sm")
    # Process the text with SpaCy
    doc = nlp(text)

    # Iterate through sentences
    for i, sentence in enumerate(doc.sents):
        #print()
        # Convert sentence to lowercase for case-insensitive search
        sentence_lower = sentence.text.lower()
        #print(sentence_lower.split())
        # Check the similarity score
        similarity_ratio = fuzz.partial_ratio("escritura publica", sentence_lower)
        # Check if "ESCRITURA PUBLICA" is in the sentence
        if similarity_ratio >= threshold:
            #print(similarity_ratio, '\n')

            # Get the substring after "ESCRITURA PUBLICA"
            #index = sentence_lower.find("escritura publica")
            result = text[i:].strip()
            if i + 3 < len(list(doc.sents)):
                #result = text[index:].strip()
                #result = list(doc.sents)[i].text.strip() + list(doc.sents)[i + 1].text.strip()
                #result = result + list(doc.sents)[i + 2].text.strip()
                #result = result + list(doc.sents)[i + 3].text.strip()
                result = result.lower()
                words_to_replace = [word for word in result.split() if fuzz.ratio(string1, 
                                                                                          word) >= threshold]
                #print(words_to_replace)
                for word in words_to_replace:
                    result = result.replace(word, string1)

                #print(result)
                return result
                
            else:
                return None
        


    # Return None if "ESCRITURA PUBLICA" is not found in any sentence
    return None
# Find string1 in string2 and extract "cant_caracters" 
# characters after string1 (including string1).
def extract_info_2(string1, string2, cant_caracters):
    """
    Parameters:
    - string1: The target string to find.
    - string2: The string to search within.
    - cant_caracters: quantity of characters to be extracting after the word string1
    Returns:
    - The extracted substring.
    """
    index = string2.find(string1)
    
    if index != -1:
        # If string1 is found, extract 50 characters after it (including string1)
        extracted_substring = string2[index:index + len(string1) + cant_caracters]
        return extracted_substring
    else:
        # If string1 is not found, return None or handle accordingly
        return None
# Extract text from image based pdf using Google Cloud vision ai API    
def google_extract(credentials_path, pdf_path, page_number):
    # Credentials to use the google api
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = vision.ImageAnnotatorClient(credentials=credentials)
    with open(pdf_path, 'rb') as pdf:
        pages = convert_from_bytes(pdf.read()) 
    page = pages[page_number - 1]
        
    full_text = ""
    image_bytes = io.BytesIO()
    page.save(image_bytes, format='PNG')
    image_content = image_bytes.getvalue()
    image = vision.Image(content=image_content)
    response = client.document_text_detection(image=image)
    full_text += response.full_text_annotation.text
    return full_text
    