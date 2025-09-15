import os
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from pathlib import Path
from .models import Product
from .serializers import ProductSerializer
from .utils.pdf_utils import fill_guest_registration_pdf, dict_map
from datetime import datetime
import shutil
from django.db.models import Max

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
    recipient_list = [settings.EMAIL_HOST_USER]

    # Ensure that path_pdf is a Path object
    if isinstance(path_pdf, str):
        path_pdf = Path(path_pdf)

    # Check if the file exists before sending
    if not path_pdf.exists():
        print(f"Error: File does not exist: {path_pdf}")
        return

    try:
        # Create an EmailMessage object
        email = EmailMessage(subject, message, email_from, recipient_list)

        # Attach the file with a proper filename and content type
        with open(path_pdf, 'rb') as f:
            email.attach(path_pdf.name, f.read(), 'application/zip')  # Corrected to ensure proper attachment as zip

        # Send the email
        email.send()
        print(f"Email sent successfully with attachment: {path_pdf}")

    except Exception as e:
        print(f"Error sending email: {e}")
        send_form_failed_email()


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
    counter = 1
    for idx in range(id_start, id_end + 1):
        try:
            product = get_object_or_404(Product, id=idx)
            serializer = ProductSerializer(product)
            product_data = serializer.data
            product_data = format_date_fields(product_data)

            print(product_data)

            # Generate the PDF and save it in the forms folder
            pdf_out = form_folder / f'form_{counter:02}.pdf'
            print('Filling the form!')
            pdf_out = fill_guest_registration_pdf(product_data, form_template, dict_map, file_out=pdf_out)
            print(f'Successfully saved: {pdf_out}')
            counter += 1
        except Exception as e:
            print(f"Error processing product ID {idx}: {e}")
            continue

    """Zipping the forms folder and sending the email"""
    try:
        # Create a zip archive of the forms folder
        print('Creating zip file...')
        zip_filename = form_folder.parent / 'forms'  # Specify the path without .zip extension
        shutil.make_archive(zip_filename, 'zip', form_folder)  # Creates forms.zip
        zip_path = f"{zip_filename}.zip"
        print(f'Zip file created at: {zip_path}')

        # Verify that the zip file exists before sending
        if not Path(zip_path).exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")

        # Send the zip file as an email attachment
        send_email_with_attachment(Path(zip_path))
        print('Email sent successfully with the attachment.')

        # Remove the forms folder after zipping
        shutil.rmtree(form_folder)
        print('Forms folder removed successfully.')

    except Exception as e:
        send_form_failed_email()
        print("Couldn't send email.")
        print(f"Error details: {e}")

    return Response('submitted')


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        return Response('STORE GET REQUEST')
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data  # returns a dictionary of the data

        # Get the current maximum lfdnr value from the Product model and increment it by one
        max_lfdnr = Product.objects.aggregate(Max('lfdnr'))['lfdnr__max'] or 0
        new_lfdnr = max_lfdnr + 1

        # Add the new lfdnr value to the validated data
        serializer.validated_data['lfdnr'] = new_lfdnr

        # Save the new product entry with the updated lfdnr value
        Product(**serializer.validated_data).save()

        """Sending EMAIL"""
        try:
            form_template = Path('savetodb/static/form_template.pdf')
            pdf_out = fill_guest_registration_pdf(serializer_data, form_template, dict_map)
            send_email_with_attachment(pdf_out) #THIS MIGHT FAIL AT TIMES
            os.remove(pdf_out)
        except Exception as e:
            # send_form_failed_email() #THIS MIGHT FAIL AT TIMES
            print("Couldn't send email.")
            print(e)

        return Response('submitted')


@api_view()
def productDetail(request, id):
    try:
        # Return a response indicating the ID cannot be provided for security or policy reasons
        return Response('ID CAN NOT BE PROVIDED')
    except Product.DoesNotExist:
        return Response(status=404)
