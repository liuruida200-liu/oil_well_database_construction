import pdfplumber
import os
import re
import requests

pdf_dir = './data/'
text_dir = './texted/'

def convert2text():
    for file in os.listdir(pdf_dir):
        with pdfplumber.open(f'./data/{file}') as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            txt_name = file.replace('.pdf', '.txt')
            with open(f'texted/{txt_name}', 'w') as f:
                f.write(text)


def parse_well_text(text_content):
    results = {
        "Date Stimulated": "N/A",
        "Stimulated Formation": "N/A",
        "Top(Ft)": "0",
        "Bottom(Ft)": "0",
        "Stimulation Stages": "0",
        "Volume": "0",
        "Volume Units": "N/A"
    }

    # 1. Extract Date Stimulated (Matches MM/DD/YYYY)
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text_content)
    if date_match:
        results["Date Stimulated"] = date_match.group(1)

    # 2. Extract Formation (Looks for 'Bakken' or text after 'Stimulated Formation')
    formation_match = re.search(r'Stimulated Formation\s+([a-zA-Z]+)', text_content)
    if formation_match:
        results["Stimulated Formation"] = formation_match.group(1)

    # 3. Extract Numeric Values (Volume, Top, Bottom)
    # Note: We remove commas during extraction to meet the numeric requirement
    volume_match = re.search(r'Volume\s+([\d,]+)', text_content)
    if volume_match:
        results["Volume"] = volume_match.group(1).replace(',', '')

    return results

if __name__ == "__main__":
    count = 1
    for raw_file in os.listdir(text_dir):
        with open(text_dir + raw_file, 'r', encoding='utf-8') as file:
            text_content = file.read()
            a = parse_well_text(text_content)
            print(str(count) + ":-----------------------")
            print(a)
            count +=1