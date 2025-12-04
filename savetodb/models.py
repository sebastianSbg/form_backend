from django.db import models


class Product(models.Model):
    # New fields from JSON
    stay_valid = models.BooleanField(default=False)
    stay_arrival_date = models.DateField(null=True, blank=True)
    stay_departure_date = models.DateField(null=True, blank=True)
    stay_num_of_guests = models.IntegerField(null=True, blank=True)

    # Assuming a max of 5 persons based on provided JSON structure
    person_first_name_0 = models.CharField(max_length=255, blank=True)
    person_last_name_0 = models.CharField(max_length=255, blank=True)
    person_country_0 = models.CharField(max_length=255, blank=True)
    person_sex_0 = models.CharField(max_length=10, blank=True)
    person_birth_date_0 = models.DateTimeField(null=True, blank=True)

    person_first_name_1 = models.CharField(max_length=255, blank=True)
    person_last_name_1 = models.CharField(max_length=255, blank=True)
    person_country_1 = models.CharField(max_length=255, blank=True)
    person_sex_1 = models.CharField(max_length=10, blank=True)
    person_birth_date_1 = models.DateTimeField(null=True, blank=True)

    person_first_name_2 = models.CharField(max_length=255, blank=True)
    person_last_name_2 = models.CharField(max_length=255, blank=True)
    person_country_2 = models.CharField(max_length=255, blank=True)
    person_sex_2 = models.CharField(max_length=10, blank=True)
    person_birth_date_2 = models.DateTimeField(null=True, blank=True)

    person_first_name_3 = models.CharField(max_length=255, blank=True)
    person_last_name_3 = models.CharField(max_length=255, blank=True)
    person_country_3 = models.CharField(max_length=255, blank=True)
    person_sex_3 = models.CharField(max_length=10, blank=True)
    person_birth_date_3 = models.DateTimeField(null=True, blank=True)

    person_first_name_4 = models.CharField(max_length=255, blank=True)
    person_last_name_4 = models.CharField(max_length=255, blank=True)
    person_country_4 = models.CharField(max_length=255, blank=True)
    person_sex_4 = models.CharField(max_length=10, blank=True)
    person_birth_date_4 = models.DateTimeField(null=True, blank=True)

    addr_street = models.CharField(max_length=255, blank=True)
    addr_valid = models.BooleanField(default=False)
    addr_city = models.CharField(max_length=255, blank=True)
    addr_zip = models.CharField(max_length=20, blank=True)
    addr_country = models.CharField(max_length=255, blank=True)

    id_number = models.CharField(max_length=255, blank=True)
    id_valid = models.BooleanField(default=False)
    id_issue_date = models.DateTimeField(null=True, blank=True)
    id_institution = models.CharField(max_length=255, blank=True)
    id_country = models.CharField(max_length=255, blank=True)

    signature = models.TextField(blank=True)
    signature_date = models.DateTimeField(null=True, blank=True)

    abnb_id = models.CharField(max_length=255, blank=True)
    abnb_name = models.CharField(max_length=255, blank=True)

    # New field lfdnr that must be zero or greater
    lfdnr = models.IntegerField(default=0, blank=True, null=True)

    # Added 2025-11-08 SBQS
    email = models.CharField(max_length=255, blank=True)
    marketing_consent = models.BooleanField(default=False)
    for_business = models.BooleanField(default=False)
