import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail, EmailMessage, get_connection
from django.conf import settings
from pathlib import Path
from .models import Product
from .serializers import ProductSerializer
from .utils.pdf_utils import fill_guest_registration_pdf, dict_map
from datetime import datetime

import shutil
from django.db.models import Max

def send_form_failed_email():
    print("Sending form failed")
    # subject = 'Form FAILED'
    # message = 'A new form failed to be submitted.'
    # email_from = settings.EMAIL_HOST_USER
    # recipient_list = [settings.EMAIL_HOST_USER]
    # send_mail(subject, message, email_from, recipient_list)

def send_email_with_attachment(path_pdf: Path):

    """Verify that file exists"""
    # Ensure that path_pdf is a Path object
    if isinstance(path_pdf, str):
        path_pdf = Path(path_pdf)

    # Check if the file exists before sending
    if not path_pdf.exists():
        print(f"Error: File does not exist: {path_pdf}")
        return

    """Selecting SMTP or SendGrid API send"""
    subject = 'Meldezettel'
    message = 'Im Anhang finden Sie die Meldezettel. <br> Mit freundlichen Grüßen <br> MSc. Sebastian Bommer, M.Sc.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.EMAIL_HOST_RECIPIENT]

    """Send VIA SMTP"""

    if not settings.EMAIL_USE_API:
        print("Sending via SMTP")
        try:
            # Create an EmailMessage object
            print("Generating email")
            email = EmailMessage(subject, message, email_from, recipient_list)

            # Attach the file with a proper filename and content type
            with open(path_pdf, 'rb') as f:
                print("Attaching to email")
                email.attach(path_pdf.name, f.read(), 'application/zip')  # Corrected to ensure proper attachment as zip

            connection = get_connection(timeout=10)  # needed if email doesn't send
            email.connection = connection
            email.send()  # THIS SEND OPERATION FAILS

        except Exception as e:
            print(f"Error sending email: {e}")
            # send_form_failed_email()

    else:
        with open(path_pdf, 'rb') as f:
            file_data = f.read()
            encoded_file = base64.b64encode(file_data).decode()  # SendGrid needs base64 string

        message = Mail(
            from_email=settings.EMAIL_HOST_USER,
            to_emails=settings.EMAIL_HOST_RECIPIENT,
            subject=subject,
            html_content=message)

        attached_file = Attachment(
            FileContent(encoded_file),
            FileName(path_pdf.name),
            FileType('application/zip'),  # Adjust MIME type if needed
            Disposition('attachment')
        )

        message.attachment = attached_file

        try:
            sg = SendGridAPIClient(settings.EMAIL_API_PASSWORD)
            # sg.set_sendgrid_data_residency("eu")
            # uncomment the above line if you are sending mail using a regional EU subuser
            response = sg.send(message)
            print(f"Successfully sent E-Mail")
        except Exception as e:
            print(e.message)


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
    abnb_id = ''

    # Generate PDFs for each product ID in the specified range
    counter = 1
    for idx in range(id_start, id_end + 1):
        try:
            product = get_object_or_404(Product, id=idx)
            serializer = ProductSerializer(product)
            product_data = serializer.data
            product_data = format_date_fields(product_data)

            if counter == 1:
                abnb_id = product_data['abnb_id']

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

        old_name = Path(zip_path)
        new_name = old_name.parent / f"forms_{datetime.today().strftime('%Y-%m-%d')}_{abnb_id}.zip"
        old_name.rename(new_name)

        zip_path = new_name

        print(f'Zip file created at: {str(zip_path)}')

        # Verify that the zip file exists before sending
        if not Path(zip_path).exists():
            print("Zip file not found")
            raise FileNotFoundError(f"Zip file not found: {zip_path}")

        # Send the zip file as an email attachment
        send_email_with_attachment(Path(zip_path))
        print('Email sent successfully with the attachment.')

        # Remove the forms folder after zipping
        shutil.rmtree(form_folder)
        print('Forms folder removed successfully.')

    except Exception as e:
        # send_form_failed_email()  # There can be issues if too many emails are sent
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
        product = Product.objects.create(**serializer.validated_data, lfdnr=0)  #TODO: fix
        serializer_data = ProductSerializer(product).data  # returns a dictionary of the data
        serializer_data = format_date_fields(serializer_data)

        # Get the current maximum lfdnr value from the Product model and increment it by one
        max_lfdnr = Product.objects.aggregate(Max('lfdnr'))['lfdnr__max'] or 0
        new_lfdnr = max_lfdnr + 1

        # Add the new lfdnr value to the validated data
        serializer.validated_data['lfdnr'] = new_lfdnr

        # Save the new product entry with the updated lfdnr value
        Product(**serializer.validated_data).save()

        """Sending EMAIL"""
        try:
            print("Sending EMAIL")
            form_template = Path('savetodb/static/form_template.pdf')
            pdf_out = fill_guest_registration_pdf(serializer_data, form_template, dict_map)
            old_name = pdf_out
            new_name = pdf_out.parent / f"register_{datetime.today().strftime("%Y-%m-%d")}_{serializer_data['abnb_id']}_{serializer_data['email']}.pdf"
            old_name.rename(new_name)
            print(f"Sending PDF via email: {pdf_out} and ABNB ID IS: {serializer_data['abnb_id']} and name is {serializer_data['abnb_name']}")
            send_email_with_attachment(new_name)
            os.remove(new_name)
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
