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


def send_form_submitted_email():
    subject = 'Form Submitted'
    message = 'A new form was just submitted.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['sebastian.bommer.sbg@gmail.com']

    send_mail(subject, message, email_from, recipient_list)


def send_email_with_attachment():
    subject = 'Email Subject'
    message = 'Email message body'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['recipient@example.com', ]

    # Create an EmailMessage object
    email = EmailMessage(subject, message, email_from, recipient_list)

    # Attach a file
    file_path = 'savetodb/static/dog.jpg'  # Update with your file path
    print(f"File exists: {Path(file_path).exists()}")
    with open(file_path, 'rb') as f:
        email.attach('Form.jpg', f.read())

    # Send the email
    email.send()


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        return Response('STORE GET REQUEST')
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)  # returns a dictionary of the data
        Product(**serializer.validated_data).save()
        try:
            # send_form_submitted_email()
            send_email_with_attachment()
        except:
            pass
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
