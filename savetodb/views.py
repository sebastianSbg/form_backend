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


@api_view(['POST'])
def send_form_email(request, id):

    product = get_object_or_404(Product, id=id)
    serializer = ProductSerializer(product)
    product_data = serializer.data

    """Sending EMAIL"""
    try:
        form_template = Path('savetodb/static/form_template.pdf')
        pdf_out = fill_guest_registration_pdf(product_data, form_template, dict_map)
        send_email_with_attachment(pdf_out)
        os.remove(pdf_out)
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
