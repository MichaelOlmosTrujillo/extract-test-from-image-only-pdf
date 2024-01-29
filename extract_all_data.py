import glob
from help_functions import extract_text_from_image_pdf
# Select all the paths with format .pdf
paths = glob.glob(r"data\*.pdf")
# resolution
res = 700
for pdf_path in paths:
    print(pdf_path)
    extract_text_from_image_pdf(pdf_path, res)