from django.shortcuts import render
import datetime
import pytz
import requests
from .models import ApiUser
from django.utils import timezone
from operator import itemgetter
from django.views.generic import RedirectView
from django.core.mail import send_mail


# Functions
def create_user(code, request):
    # Initial call to the drchrono API
    authorization_response = requests.post('https://drchrono.com/o/token/', data={
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8000/api/',
        'client_id': 'kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa',
        'client_secret': '8DWCWZP2YuOXONuIkTetaNHjF2nfyLmDCrbJFomGKrMJyyjJiGSdDS0rANiukFZ5Y4HSricrKLOEqEZFFMP017u6bbxVE06BE8X5EEN0Y0XKMP9ggp7ZHaCwrrD9Ecv5',
    })
    authorization_response.raise_for_status()
    api_authorization_data = authorization_response.json()

    # Call to the logged in drchrono user
    user_response = requests.get('https://drchrono.com/api/users/current', headers={
        'Authorization': 'Bearer %s' % api_authorization_data['access_token'],
    })
    user_response.raise_for_status()
    user_data = user_response.json()

    # Create the user object
    user, created = ApiUser.objects.get_or_create(username=user_data['username'])
    user.access_token = api_authorization_data['access_token']
    user.refresh_token = api_authorization_data['refresh_token']
    user.expires_timestamp = datetime.datetime.now(pytz.utc) + datetime.timedelta(
        seconds=api_authorization_data['expires_in'])
    user.save()

    # Appropriately set session variables
    request.session['username'] = user_data['username']
    request.session['logged_in'] = True

    return user


def update_user(user):
    authorization_response = requests.post('https://drchrono.com/o/token/', data={
        'refresh_token': user.refresh_token,
        'grant_type': 'refresh_token',
        'client_id': 'kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa',
        'client_secret': '8DWCWZP2YuOXONuIkTetaNHjF2nfyLmDCrbJFomGKrMJyyjJiGSdDS0rANiukFZ5Y4HSricrKLOEqEZFFMP017u6bbxVE06BE8X5EEN0Y0XKMP9ggp7ZHaCwrrD9Ecv5',
    })

    authorization_response.raise_for_status()
    api_authorization_data = authorization_response.json()

    user.access_token = api_authorization_data['access_token']
    user.save()


# Views
def home(request):
    context = {
        'title': 'Home Page',
    }

    return render(request, "home.html", context)


def api(request):
    # Create a new user object if there is no session username or the user is not logged in
    if not request.session.get('username', '') or not request.session.get('logged_in', False):
        if not request.GET.get('code'):
            return RedirectView.as_view(
                url='https://drchrono.com/o/authorize/?redirect_uri=http://localhost:8000/api/&response_type=code&client_id=kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa')(
                request)
        user = create_user(request.GET.get('code'), request)
    else:
        # Check to see if a user with the session username exists
        try:
            user = ApiUser.objects.get(username=request.session['username'])
            # Timestamp has expired
            if user.expires_timestamp < timezone.now():
                # Update the user access token
                update_user(user)
        except ApiUser.DoesNotExist:
            if not request.GET.get('code'):
                return RedirectView.as_view(
                    url='https://drchrono.com/o/authorize/?redirect_uri=http://localhost:8000/api/&response_type=code&client_id=kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa')(
                    request)
            user = create_user(request.GET.get('code'), request)

    # Patients Info
    headers = {
        'Authorization': 'Bearer ' + user.access_token,
    }

    patients = []
    patients_url = 'https://drchrono.com/api/patients'
    while patients_url:
        data = requests.get(patients_url, headers=headers).json()
        patients.extend(data['results'])
        patients_url = data['next']

    # Create a list of tuples including names, emails, and birth dates
    patient_tuples_list = []
    patients_with_birthdays = []

    for current_patient in patients:
        # Only add patients who have both an email and a birth date
        if current_patient['email'] and current_patient['date_of_birth']:
            patient_tuples_list.append((current_patient['first_name'], current_patient['last_name'],
                                        current_patient['email'], current_patient['date_of_birth']))
            # Get birth date month and day
            month = current_patient['date_of_birth'][5:7]
            day = current_patient['date_of_birth'][8:]
            # Check to see if it is the patients birth day
            # Cast to int to account for 01 != 1 and other applicable conflicts
            if int(month) == int(datetime.date.today().month) and int(day) == int(datetime.date.today().day):
                patients_with_birthdays.append(
                    (current_patient['first_name'], current_patient['last_name'], current_patient['email']))

                email_message = "Dr. Kopen wishes you, %s %s, a happy birthday!  Also, Django is pretty cool." % (
                    current_patient['first_name'],
                    current_patient['last_name'])

                send_mail('Happy Birthday!', email_message, 'api@alexkopen.com', [current_patient['email']],
                          fail_silently=False)

    # Sort by DOB, which is at index 3 of each tuple
    patient_tuples_list = sorted(patient_tuples_list, key=itemgetter(3))

    context = {
        'title': 'API Home',
        'patient_tuple': patient_tuples_list,
        'birthday_tuple': patients_with_birthdays,
    }

    return render(request, "api.html", context)
