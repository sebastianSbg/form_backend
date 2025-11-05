# Django REST Starter

## TODO

- [ ] ZIP Needs to allow letters and numbers
- [ ] Add email
- [ ] One form with Airbnb ID being input
- [ ] Ask if they want bicycle rental or others
- [ ] Automatic sending of email summaries
- [ ] Create a default version with version history
- [ ] Datum eingabe sollte string sein und nicht flexibles datum (Only make them add people over tha age of 14)
- [ ] Don't allow multiple submissions
- [ ] Stier 4 not tied to Forms
- [ ] Be able to export data for analysis

### V0.1.0
- [ ] Checkin and checkout can't be on the same date
- [ ] Only entries of people 16 years or older
- [ ] Address validate to not be Airbnb address
- [ ] Arrival and departure text doesn't get updated every time field is set!
- [ ] Switch to API email send on SendGrid -> SMTP blocked on Hobby Plan


## File Structure
```
django-rest-starter/
├── main/
│   ├── __init__.py
│   ├── asgi.py
│   ├── local_settings.py
│   ├── production_settings.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── requirements.txt
├── README.md
├── manage.py
```

## Getting Started

1. Clone this repository to your local machine:
   ```shell
   git clone https://github.com/Grey-A/django-rest-starter.git
   ```

2. Navigate to the project directory:
   ```shell
   cd django-rest-starter
   ```

3. Set up a virtual environment (recommended) and install dependencies:
   ```shell
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```shell
   python manage.py migrate
   ```

5. Run the development server:
   ```shell
   python manage.py runserver
   ```

## Configuration

This project includes two settings files:

- `production_settings.py`: Configuration for when the app is live on railway, it uses PostgreSQL. 
  
NOTE: Remember to change the secret key on railway, you can use websites like `https://djecrety.ir/` to generate your new secret key

- `local_settings.py`: Configuration for local development uses a randomly generated secret key with sqlite db
  
NOTE: The DJANG_ENV variable from Railway is used to determine which settings file to use.

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute improvements, feel free to open an issue or submit a pull request.