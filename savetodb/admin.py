from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'stay_valid', 'stay_arrival_date', 'stay_departure_date', 'stay_num_of_guests',
        'person_first_name_0', 'person_last_name_0', 'person_country_0', 'person_sex_0', 'person_birth_date_0',
        'person_first_name_1', 'person_last_name_1', 'person_country_1', 'person_sex_1', 'person_birth_date_1',
        'person_first_name_2', 'person_last_name_2', 'person_country_2', 'person_sex_2', 'person_birth_date_2',
        'person_first_name_3', 'person_last_name_3', 'person_country_3', 'person_sex_3', 'person_birth_date_3',
        'person_first_name_4', 'person_last_name_4', 'person_country_4', 'person_sex_4', 'person_birth_date_4',
        'addr_street', 'addr_valid', 'addr_city', 'addr_zip', 'addr_country',
        'id_number', 'id_valid', 'id_issue_date', 'id_institution', 'id_country',
        'signature', 'signature_date', 'abnb_id', 'abnb_name'
    )
    list_filter = ('stay_valid', 'addr_valid', 'id_valid')
    search_fields = ('stay_num_of_guests', 'stay_arrival_date', 'stay_departure_date', 'person_last_name_0', 'person_first_name_0')

# You can customize more as per your requirements.
