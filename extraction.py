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


def parse_well_text(file_path):
    results = {
        "well_name": "N/A",
        "operator": "N/A",
        "enseco_job": "N/A",
        "county": "N/A",
        "latitude": "N/A",
        "longitude": "N/A",
        "datum": "N/A"
    }
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    patterns = {
        "well_name": [
            r"(?:Well|Facility)\s*Name\s*:\s*(.*)",
            r"Well Name and Number[\s\S]*?\n(?:[a-zA-Z]\s*\n)?(.*?)(?=\s+\d+\s+\d+\s+[NS])"
        ],
        "operator": [r"Well Operator : (.*?)\n"],
        "enseco_job#": [r"\bJob (\d+)\b"],              
        "county": [r"County : (.*?)\n"],         
        "latitude": [r'(\d+°\d+\'\d+\.\d+\"[NS])'], 
        "longitude": [r'(\d+°\d+\'\d+\.\d+\"[EW])'],
        "datum": [r"Vertical Datum to DDZ\s+([\d.]+ ft)"] 
        }
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results[key] = match.group(1).strip()
                break
    return results
    




if __name__ == "__main__":
    for raw_file in os.listdir(text_dir):
        f_pass = "texted/" + raw_file
        a = parse_well_text(f_pass)
        print(raw_file + ":-----------------------")
        print(a)
