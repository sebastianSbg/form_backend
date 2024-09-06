from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:id>', views.productDetail),
    path('mail/<int:id_start>/<int:id_end>/', views.send_form_email, name='send_form_email'),

]