import pdfrw
from collections import Counter
import os
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
import svgwrite
from PIL import Image
from io import BytesIO

import svgwrite
from PIL import Image
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.graphics import renderPDF, renderPM
from pathlib import Path


def render_svg_to_pdf(svg_string, pdf_file, x, y, width, height, orientation='portrait'):
    """
    Render an SVG image at a specific location and size within a PDF using svglib and reportlab.

    Parameters:
    - svg_file (str): Path to the SVG file.
    - pdf_file (str): Path to save the PDF file.
    - x (int): X-coordinate for the top-left corner of the rendered SVG.
    - y (int): Y-coordinate for the top-left corner of the rendered SVG.
    - width (int): Width of the rendered SVG.
    - height (int): Height of the rendered SVG.
    - orientation (str, optional): Orientation of the PDF ('portrait' or 'landscape'). Default is 'portrait'.
    """
    # Determine the page size based on orientation
    if orientation == 'landscape':
        page_size = landscape(letter)
    else:
        page_size = letter

    # Read SVG file into ReportLab drawing object
    drawing = svg2rlg(BytesIO(svg_string.encode()))

    # Create a PDF canvas
    c = canvas.Canvas(pdf_file, pagesize=page_size)

    # Scale the drawing to fit within the specified width and height
    drawing.scale(width / drawing.width, height / drawing.height)

    # Draw the SVG on the canvas at the specified location
    renderPDF.draw(drawing, c, x, y)

    # Save the canvas
    c.save()


# # Example usage:
# svg_string = '''
# <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
#     <rect x="10" y="10" width="80" height="80" fill="blue" />
# </svg>
# '''
# file_path = "output.png"
# svg_to_png(svg_string, file_path, width=100, height=100)


def get_pdf_field_names(pdf_file):
    template_pdf = pdfrw.PdfReader(pdf_file)
    page = template_pdf.pages[0]

    field_names = []
    if '/Annots' in page:
        annotations = page['/Annots']
        for annotation in annotations:
            if '/T' in annotation:
                field_name = annotation['/T']
            if '/V' in annotation:
                field_value = annotation['/V'][1:-1] if isinstance(annotation['/V'], pdfrw.PdfString) else annotation[
                    '/V']
            else:
                field_value = None

            field_names.append((field_name, field_value))

    return field_names


def write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict):
    ANNOT_KEY = '/Annots'
    ANNOT_FIELD_KEY = '/T'  # name
    ANNOT_FORM_type = '/FT'  # Form type (e.g. text/button)
    ANNOT_FORM_button = '/Btn'  # ID for buttons, i.e. a checkbox
    ANNOT_FORM_text = '/Tx'  # ID for textbox
    SUBTYPE_KEY = '/Subtype'
    WIDGET_SUBTYPE_KEY = '/Widget'
    try:
        template_pdf = pdfrw.PdfReader(input_pdf_path)
        i = 0
        for Page in template_pdf.pages:
            if Page[ANNOT_KEY]:
                for annotation in Page[ANNOT_KEY]:
                    if annotation[ANNOT_FIELD_KEY] and annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                        key = annotation[ANNOT_FIELD_KEY][1:-1]  # Remove parentheses
                        if key in data_dict.keys():
                            i += 1
                            if annotation[ANNOT_FORM_type] == ANNOT_FORM_button:
                                annotation.update(
                                    pdfrw.PdfDict(V=pdfrw.PdfName(data_dict[key]), AS=pdfrw.PdfName(data_dict[key])))
                            elif annotation[ANNOT_FORM_type] == ANNOT_FORM_text:
                                annotation.update(pdfrw.PdfDict(V=data_dict[key], AP=data_dict[key]))
        if i > 0:
            template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
            pdfrw.PdfWriter().write(output_pdf_path, template_pdf)
            return True
    except Exception as ex:
        print(ex)
        return False


import csv


def read_csv_file(csv_file):
    with open(csv_file, newline='', encoding='ISO-8859-1') as file:
        reader = csv.DictReader(file)
        rows_data = []

        for row in reader:
            row_dict = {}
            for key, value in row.items():
                if value:
                    row_dict[key] = str(value)
            rows_data.append(row_dict)

    return rows_data


def list_dict_mapping(mapping, column_mapping, list_in) -> dict:
    dict_out = {}
    for key, value in mapping.items():
        index = column_mapping[key]
        dict_out[value] = list_in[index]

    return dict_out


def map_dict(mapping: dict, in_dict: dict, delete_original: bool = False) -> dict:
    """Appends the key mappings to the in_dictionary"""
    dict_out = in_dict
    for key_mapping, value_mapping in mapping.items():
        if value_mapping in in_dict:
            dict_out[key_mapping] = in_dict[value_mapping]
            if delete_original:
                del dict_out[value_mapping]

    return dict_out


def flatten_form_fields(input_pdf, output_pdf):
    """Convert form fields to text in PDF"""
    template_pdf = pdfrw.PdfReader(input_pdf)
    for page in template_pdf.pages:
        annotations = page.get('/Annots')
        if annotations:
            for annotation in annotations:
                annotation.update(pdfrw.PdfDict(Ff=1))  # Set the Ff (field flags) to 1 to make the fields read-only
    pdfrw.PdfWriter().write(output_pdf, template_pdf)


def merge_pdfs_with_form_fields(pdf1_path, pdf2_path, output_path):
    # Read input PDFs
    input_pdf1 = pdfrw.PdfReader(pdf1_path)
    input_pdf2 = pdfrw.PdfReader(pdf2_path)

    # Create a writer object for the output PDF
    output_pdf = pdfrw.PdfWriter()

    # Merge pages from the first PDF
    for page in input_pdf1.pages:
        output_pdf.addpage(page)

    # Merge pages from the second PDF
    for page in input_pdf2.pages:
        output_pdf.addpage(page)

    # Preserve form fields from the second PDF (if any)
    if "/AcroForm" in input_pdf2.keys():
        output_pdf.trailer['/Root']['/AcroForm'] = input_pdf2['/AcroForm']

    # Write the merged PDF to the output file
    output_pdf.write(output_path)


# Usage example:

def create_img_pdf(pdf_out: str, img: str, **args):
    pdf = FPDF(orientation='L')

    pdf.add_page()
    pdf.image(img, **args)
    pdf.output(pdf_out)


def insert_img(pdf_in: str, pdf_out: str, img: str, **args):
    create_img_pdf('temp.pdf', img, **args)
    overlay_pdfs(pdf_in, 'temp.pdf', pdf_out, rotation=270)
    os.remove("temp.pdf")


def overlay_pdfs(original_pdf_path, overlay_pdf_path, output_pdf_path, rotation=0):
    # Read the original PDF
    original_pdf = pdfrw.PdfReader(original_pdf_path)

    # Read the overlay PDF
    overlay_pdf = pdfrw.PdfReader(overlay_pdf_path)

    # Merge the pages
    for page, overlay_page in zip(original_pdf.pages, overlay_pdf.pages):
        # Convert Rotate attribute to integer
        overlay_rotate = int(overlay_page.Rotate or 0)

        # Rotate the overlay page
        overlay_page.Rotate = overlay_rotate + rotation

        # Merge the rotated overlay page onto the original page
        pdfrw.PageMerge(page).add(overlay_page).render()

    # Write the result to the output PDF
    pdfrw.PdfWriter().write(output_pdf_path, original_pdf)


############################# CUTOM PDF FILLER ###########################

dict_map = {
    'Nachname': 'person_last_name_0',
    'Vorname': 'person_first_name_0',
    'Geburtsdatum': 'person_birth_date_0',
    'Staatsangehoerigkeit': 'person_country_0',
    'Strasse': 'addr_street',
    'Postleitzahl': 'addr_zip',
    'Gemeindename': 'addr_city',
    'Staat': 'addr_country',
    'Nummer': 'id_number',
    'Ausstellungsdatum': 'id_issue_date',
    'Ausstellende Behoerde': 'id_institution',
    'Austellungsstaat': 'id_country',
    'Vorname Gast 1': 'person_first_name_1',
    'Nachname Gast 1': 'person_last_name_1',
    'Geburtsdatum Gast 1': 'person_birth_date_1',
    'Vorname Gast 2': 'person_first_name_2',
    'Nachname Gast 2': 'person_last_name_2',
    'Geburtsdatum Gast 2': 'person_birth_date_2',
    'Vorname Gast 3': 'person_first_name_3',
    'Nachname Gast 3': 'person_last_name_3',
    'Geburtsdatum Gast 3': 'person_birth_date_3',
    'Vorname Gast 4': 'person_first_name_4',
    'Nachname Gast 4': 'person_last_name_4',
    'Geburtsdatum Gast 4': 'person_birth_date_4',
    'Airbnb Ankunftstag': 'stay_arrival_date',
    'abreisetag_geplant': 'stay_departure_date',
    'Gesamtanzahl': 'stay_num_of_guests',
    'Signature Datum': 'signature_date',
    'UnterkunftName': 'abnb_name',
    'Kennzahl': 'abnb_id',
}


def format_date_to_string(data):
    if isinstance(data, datetime):
        return data.strftime("%d-%m-%Y")
    return data


def fill_guest_registration_pdf(data: dict, path_form_template: Path, mapping_data: dict = None,
                                file_out: Path = "temp.pdf", lfdnr: int = 0) -> Path:
    out_path = file_out.resolve()
    data_transformed = map_dict(mapping_data, data, delete_original=False) if dict_map else data

    """ABNB INFO"""

    data_transformed['LfdNr'] = str(lfdnr)

    try:

        """SEX"""

        mapSex = {'Male': 'SexM', 'Female': 'SexW', 'divers': 'SexD', 'inter': 'SexI',
                  'keine Angabe': 'SexK', 'Other': 'SexO'}
        data_transformed[mapSex[data_transformed['person_sex_0']]] = 'Yes'

        data_transformed['Nachname.2'] = "Bomml"

        """Abreisetage"""
        data_transformed['abreisetag_wirklich'] = data_transformed['abreisetag_geplant']

        """Laender"""
        countries = []
        for i in range(5):
            if f'person_country_{i}' in data_transformed:
                countries.append(data_transformed[f'person_country_{i}'])

        for i2, (key, value) in enumerate(Counter(countries).items()):
            if key:
                data_transformed[f'Land{i2 + 1}'] = str(key)
                data_transformed[f'LandZahl{i2 + 1}'] = str(value)

        for key, value in data_transformed.items():
            data_transformed[key] = format_date_to_string(value)

        data_transformed['Gesamtanzahl'] = str(data_transformed['Gesamtanzahl'])

        print("Gesamtanzahl")
        print(data_transformed['Gesamtanzahl'])
        print(data_transformed['stay_num_of_guests'])
        write_fillable_pdf(str(path_form_template), str(out_path), data_transformed)
        flatten_form_fields(str(out_path), str(out_path))

    except Exception as e:
        pass

    """Insert signature"""

    try:
        path_img_pdf = str(out_path.parent.resolve() / 'img.pdf')
        # render_svg_to_pdf(data_transformed['signature'], path_img_pdf, 625, 80, 75, 30, orientation='landscape')
        render_svg_to_pdf(data_transformed['signature'], path_img_pdf, 615, 95, 50, 20, orientation='landscape')
        overlay_pdfs(str(out_path.resolve()), path_img_pdf, str(out_path.resolve()), rotation=270)
        # os.remove(path_img_pdf)
    except Exception as e:
        print("Couldn't perform signature")
        print(e)

    return out_path


if __name__ == "__main__":

    pdf_template = 'template.pdf'
    csv_file = "gaeste_merged.csv"  # Replace with the path to your CSV file

    print(get_pdf_field_names(pdf_template))

    rows_data = read_csv_file(csv_file)

    mapping_key_csv_value_field = {  # TODO: maske sure mapping is correct
        'Familienname': 'Nachname',
        'Vorname': 'Vorname',
        'Geburtsdatum': 'Geburtsdatum',
        'Staatsangehoerigkeit': 'Staatsangehoerigkeit',
        'Strasse und Hausnummer': 'Strasse',
        'Postleitzahl': 'Postleitzahl',
        'Gemeindename': 'Gemeindename',
        'Staat': 'Staat',
        'Nummer': 'Nummer',
        'Ausstellungsdatum': 'Ausstellungsdatum',
        'Ausstellende Behoerde': 'Ausstellende Behoerde',
        'Vorname.1': 'Vorname Gast 1',
        'Nachname': 'Nachname Gast 1',
        'Geburtsdatum.1': 'Geburtsdatum Gast 1',
        'Vorname.2': 'Vorname Gast 2',
        'Nachname.1': 'Nachname Gast 2',
        'Geburtsdatum.2': 'Geburtsdatum Gast 2',
        'Vorname.3': 'Vorname Gast 3',
        'Nachname.2': 'Nachname Gast 3',
        'Geburtsdatum.3': 'Geburtsdatum Gast 3',
        'Vorname.4': 'Vorname Gast 4',
        'Nachname.3': 'Nachname Gast 4',
        'Geburtsdatum.4': 'Geburtsdatum Gast 4',
        'Airbnb Ankunftstag': 'Airbnb Ankunftstag',
        'Staat.1': 'Austellungsstaat',
        'Airbnb Abreisetag (geplant)': 'abreisetag_geplant',
        'Airbnb Abreisetag (tatsaechlich)': 'abreisetag_wirklich',
        'Gesamtanzahl': 'TBD',
        'Signature Datum': 'TBD'  # TODO: why not available?
    }

    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        column_mapping = {name: i for i, name in enumerate(next(reader))}  # Skip the header row
        for i, guest in enumerate(reader):
            guest_info = list_dict_mapping(mapping_key_csv_value_field, column_mapping, guest)

            """Laender"""
            countries = [guest[column_mapping[i]].upper().strip() for i in
                         ['Staat', 'Herkunftsland', 'Herkunftsland.1', 'Herkunftsland.3', 'Herkunftsland.2']]

            total_guests = 0
            for i2, (key, value) in enumerate(Counter(countries).items()):
                if key:
                    guest_info[f'Land{i2 + 1}'] = str(key)
                    guest_info[f'LandZahl{i2 + 1}'] = str(value)
                    total_guests += value

            """Anzahl Gaeste"""
            guest_info['Gesamtanzahl'] = total_guests

            """Geschlaecht"""
            mapSex = {'maennlich': 'SexM', 'weiblich': 'SexW', 'divers': 'SexD', 'inter': 'SexI',
                      'keine Angabe': 'SexK', 'offen': 'SexO'}
            guest_info[mapSex[guest[column_mapping['Geschlaecht']]]] = 'Yes'

            """ID"""
            guest_info['Kennzahl'] = '50305-000003-2023'
            guest_info['UnterkunftName'] = 'Airbnb Bommer'
            guest_info['LfdNr'] = str(i + 1)

            """Datum"""
            guest_info['Signature Datum'] = str(guest[column_mapping['Timestamp_x']].split(' ')[0])  # TODO: check index

            """Write"""
            current_datetime = datetime.now()
            datetime_string = current_datetime.strftime("%Y%m%d%H%M")

            pdf_dir = Path(f"guest_{datetime_string}")
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)

            pdf_name = pdf_dir / f"gast{i}.pdf"

            write_fillable_pdf(pdf_template, pdf_name, guest_info)
            flatten_form_fields(pdf_name, pdf_name)

            signature = None
            if guest[column_mapping['ManualSig']]:
                signature = guest[column_mapping['ManualSig']]
            if guest[column_mapping['Your Signature']]:
                signature = guest[column_mapping['Your Signature']]  # TODO: add electronic sig if not available

            if signature:
                print(signature)
                insert_img(pdf_name, pdf_name, signature, x=217, y=177, h=10)
