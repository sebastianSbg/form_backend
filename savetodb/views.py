from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer

from rest_framework import status

# Create your views here.

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        return Response('STORE GET REQUEST')
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)  # returns a dictionary of the data
        Product(**serializer.validated_data).save()
        return Response('submitted')


@api_view()
def productDetail(request, id):
    try:
        # product = Product.objects.get(pk=id)
        # serializer = ProductSerializer(product)
        # return Response(serializer.data)
        return Response('ID CAN"T BE PROVIDED')
    except Product.DoesNotExist:
        return Response(status=404)