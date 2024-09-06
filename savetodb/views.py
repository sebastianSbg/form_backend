import os

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.conf import settings
from pathlib import Path
from .utils.pdf_utils import fill_guest_registration_pdf, dict_map
from django.shortcuts import get_object_or_404
from datetime import datetime
import shutil

def send_form_failed_email():
    subject = 'Form FAILED'
    message = 'A new form failed to be submitted.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_USER]

    send_mail(subject, message, email_from, recipient_list)


def send_email_with_attachment(path_pdf: Path):
    subject = 'Form submitted'
    message = 'Successfully submitted form.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_USER, ]

    # Create an EmailMessage object
    email = EmailMessage(subject, message, email_from, recipient_list)

    # Attach a file
    print(f"File exists: {path_pdf.exists()}")
    with open(path_pdf, 'rb') as f:
        email.attach('Form.pdf', f.read())

    # Send the email
    email.send()


def format_date_fields(data):
    for key, value in data.items():
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                continue
        if isinstance(value, datetime):
            data[key] = value.strftime("%d-%m-%Y")
    return data

@api_view(['GET'])
def send_form_email(request, id_start, id_end):
    form_template = Path('savetodb/static/form_template.pdf')
    form_folder = Path('savetodb/static/forms')
    form_folder.mkdir(parents=True, exist_ok=True)  # Create forms folder if it doesn't exist

    # Generate PDFs for each product ID in the specified range
    for idx in range(id_start, id_end + 1):
        try:
            product = get_object_or_404(Product, id=idx)
            serializer = ProductSerializer(product)
            product_data = serializer.data
            product_data = format_date_fields(product_data)

            # Generate the PDF and save it in the forms folder
            pdf_out = form_folder / f'form_{idx}.pdf'
            fill_guest_registration_pdf(product_data, form_template, dict_map, file_out=pdf_out)
            print(f'saved: {pdf_out}')
        except Exception as e:
            print(f"Error processing product ID {idx}: {e}")
            continue

    """Zipping the forms folder and sending the email"""
    try:
        # Create a zip archive of the forms folder
        print('stop 1')
        zip_filename = form_folder.parent / 'forms'  # Specify the path without .zip extension
        print('stop 2')
        shutil.make_archive(zip_filename, 'zip', form_folder)  # Creates forms.zip
        print('stop 3')
        # Send the zip file as an email attachment
        # Verify that the zip file exists before sending
        zip_path = f"{zip_filename}.zip"
        if not Path(zip_path).exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")

        # Send the zip file as an email attachment
        send_email_with_attachment(Path(zip_path))
        print('stop 4')
        # Remove the forms folder after zipping
        shutil.rmtree(form_folder)

    except Exception as e:
        send_form_failed_email()
        print("Couldn't send email.")
        print(e)

    return Response('submitted')


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        return Response('STORE GET REQUEST')
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data  # returns a dictionary of the data
        Product(**serializer.validated_data).save()

        """Sending EMAIL"""
        try:
            form_template = Path('savetodb/static/form_template.pdf')
            pdf_out = fill_guest_registration_pdf(serializer_data, form_template, dict_map)
            send_email_with_attachment(pdf_out)
            os.remove(pdf_out)
        except Exception as e:
            send_form_failed_email()
            print("Couldn't send email.")
            print(e)

        return Response('submitted')


@api_view()
def productDetail(request, id):
    try:
        # product = Product.objects.get(pk=id)
        # serializer = ProductSerializer(product)
        # return Response(serializer.data)
        return Response('ID CAN NOT BE PROVIDED')
    except Product.DoesNotExist:
        return Response(status=404)
