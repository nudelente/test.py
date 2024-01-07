import os
import PyPDF2
import re

def parse_date(date_str):
    # Funktion zum Parsen verschiedener Datumsformate
    # Versuche das Format "DD.MM.YYYY"
    match = re.match(r'(\d{2})[.-](\d{2})[.-](\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"
    return None


def extract_invoice_number(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        lines = text.split("\n")
        keywords = ["Invoice #", "Numero fattura", "Numéro de la facture", "Rechnungsnummer", "Número de la factura", "Número de la nota de crédito", "Numéro de l'avoir"]
        for line in lines:
            if any(line.startswith(keyword) for keyword in keywords):
                words = line.split(" ")
                invoice_num = words[-1]
                print(f"Found invoice number: {invoice_num}")
                return invoice_num
    print("No invoice number found.")
    return None

def extract_date_from_pdf(file_path, language):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        lines = text.split("\n")

    date_keywords = {
        "DE": "/Lieferdatum",
        "IT": "Data di fatturazione / Data di consegna",
        "ES": "Fecha de la factura/Fecha de la entrega",
        "FR": "Date de la facture/Date de la livraison",
        "UK": "Invoice date / Delivery date"
    }
    keyword = date_keywords[language]
    for line in lines:
        if keyword in line:
            words = line.split()
            if len(words) >= 3:
                day = words[-3]
                month = words[-2]
                year = words[-1]

                print(f"Debugging: day={day}, month={month}, year={year}")

                month_dict = {
                    "Januar": "01", "Februar": "02", "März": "03", "April": "04", "Mai": "05", "Juni": "06",
                    "Juli": "07", "August": "08", "September": "09", "Oktober": "10", "November": "11", "Dezember": "12",
                    "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04", "maggio": "05", "giugno": "06",
                    "luglio": "07", "agosto": "08", "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12",
                    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
                    "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
                    "janvier": "01", "février": "02", "mars": "03", "avril": "04", "mai": "05", "juin": "06",
                    "juillet": "07", "août": "08", "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
                    "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
                    "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
                }

                formatted_date = f"{month_dict[month]}-{day}-{year}"
                print(f"Found date: {formatted_date}")
                return formatted_date

    print(f"Date keyword not found for language {language}")

    return None


def process_pdf_files(pdf_dir):
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, filename)

            # Check if the file is already correctly named
            if re.match(r'\d{2}-\d{2}-\d{4}_[A-Z]{2}_[A-Z0-9]+\.pdf', filename):
                print(f"File already correctly named: {filename}")
                continue

            # Value 1: Rechnungsnummer
            invoice_number = extract_invoice_number(file_path)

            # Value 2: Datum
            new_filename = None
            for language in ["DE", "IT", "ES", "FR", "UK"]:
                formatted_date = extract_date_from_pdf(file_path, language)
                if formatted_date:
                    new_filename = f"{formatted_date}_{language}_{invoice_number}.pdf"
                    break

            if new_filename:
                # Überprüfen, ob die Datei bereits existiert
                target_path = os.path.join(pdf_dir, new_filename)

                # Check if the target file already exists and if it has the correct name
                if not os.path.exists(target_path):
                    # Handle the case where the target file already exists
                    counter = 1
                    while os.path.exists(target_path):
                        new_filename = f"{formatted_date}_{language}_{invoice_number}_{counter}.pdf"
                        target_path = os.path.join(pdf_dir, new_filename)
                        counter += 1

                    # Umbenenne die Datei
                    os.rename(file_path, target_path)
                    print(f"Renamed: {filename} -> {new_filename}")
            else:
                # Wenn kein Datum für die deutsche Sprache gefunden wurde, benutze einen anderen Dateinamen
                new_filename = f"no_date_DE_{invoice_number}.pdf"
                target_path = os.path.join(pdf_dir, new_filename)

                # Check if the target file already exists and if it has the correct name
                if not os.path.exists(target_path):
                    # Handle the case where the target file already exists
                    counter = 1
                    while os.path.exists(target_path):
                        new_filename = f"no_date_DE_{invoice_number}_{counter}.pdf"
                        target_path = os.path.join(pdf_dir, new_filename)
                        counter += 1

                    os.rename(file_path, target_path)
                    print(f"No date found for {filename}. Renamed to: {new_filename}")


# Beispielaufruf
pdf_directory = "."
process_pdf_files(pdf_directory)



