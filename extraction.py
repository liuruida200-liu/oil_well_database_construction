import pdfplumber
import os
import re
import requests
import mysql.connector

pdf_dir = './data/'
text_dir = './texted/'


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="520529",
        database="560_lab6"
    )


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS well_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255),
            well_name VARCHAR(255),
            api VARCHAR(255),
            operator VARCHAR(255),
            enseco_job VARCHAR(255),
            county VARCHAR(255),
            latitude VARCHAR(255),
            longitude VARCHAR(255),
            datum VARCHAR(255)mysql -u root -p
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def save_to_db(file_name, data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO well_data 
            (file_name, well_name, api, operator, enseco_job, county, latitude, longitude, datum)
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        file_name,
        data["well_name"],
        data["api"],
        data["operator"],
        data["enseco_job"],
        data["county"],
        data["latitude"],
        data["longitude"],
        data["datum"]
    )
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()



def convert2text():
    for file in os.listdir(pdf_dir):
        with pdfplumber.open(f'./data/{file}') as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            txt_name = file.replace('.pdf', '.txt')
            with open(f'texted/{txt_name}', 'w') as f:
                f.write(text)

def clean_well_name(name_str):
    tokens = name_str.split()
    cut = len(tokens)
    seen_number = False
    for i, token in enumerate(tokens):
        if re.search(r'\d', token):
            seen_number = True
        elif seen_number and re.match(r'^[A-Za-z]+$', token):
            cut = i
            break
    return ' '.join(tokens[:cut])


def parse_well_text(file_path):
    results = {
        "well_name": "N/A",
        "api": "N/A",
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
            r"Well Name\s*:\s*(.*)\n",
            r"Well Name and Number[\s\S]*?\n(?:[a-zA-Z]\s*\n)?(.*?)(?=\s+\d+\s+\d+\s+[NS])"
        ],
        "api":[r"API#:\s*(.*?)\n"],
        "operator": [r"Well Operator : (.*?)\n"],
        "enseco_job": [r"\bJob (\d+)\b"],
        "county": [r"County : (.*?)\n"],         
        "latitude": [r'(\d+°\d+\'\d+\.\d+\"[NS])'], 
        "longitude": [r'(\d+°\d+\'\d+\.\d+\"[EW])'],
        "datum": [r"Vertical Datum to DDZ\s+([\d.]+ ft)"] 
    }
    
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_value = match.group(1).strip()
                if key == "well_name":
                    extracted_value = clean_well_name(extracted_value)
                    
                results[key] = extracted_value
                break
                
    return results
    



if __name__ == "__main__":
    create_table()
    for raw_file in os.listdir(text_dir):
        f_pass = "texted/" + raw_file
        a = parse_well_text(f_pass)
        print(raw_file + ":-----------------------")
        print(a)
        save_to_db(raw_file, a)