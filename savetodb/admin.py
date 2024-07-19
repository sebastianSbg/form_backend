from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'stay_arrival_date', 'stay_departure_date', 'stay_num_of_guests',
        'person_first_name_0', 'person_last_name_0', 'person_country_0', 'person_sex_0', 'person_birth_date_0',
        'person_first_name_1', 'person_last_name_1', 'person_country_1', 'person_sex_1', 'person_birth_date_1',
        'person_first_name_2', 'person_last_name_2', 'person_country_2', 'person_sex_2', 'person_birth_date_2',
        'addr_street', 'addr_city', 'addr_zip', 'addr_country',
        'id_number', 'id_issue_date', 'id_institution', 'id_country', 'signature_date',
    )
    list_filter = ('stay_num_of_guests',)
    search_fields = ('stay_num_of_guests', 'stay_arrival_date', 'stay_departure_date', 'person_last_name_0', 'person_first_name_0')

# You can customize more as per your requirements.
