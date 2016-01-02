from django.shortcuts import render
import datetime, pytz, requests
import json
from .models import ApiUser
from django.utils import timezone


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


# Views
def home(request):
    title = 'Home Page'

    context = {
        'title': title,
    }

    return render(request, "home.html", context)


def api(request):
    # Create a new user object if there is no session username or the user is not logged in
    if not request.session.get('username', '') or not request.session.get('logged_in', False):
        if not request.GET.get('code'):
            return render(request, '/login')
        user = create_user(request.GET.get('code'), request)
    else:
        # Check to see if a user with the session username exists
        try:
            user = ApiUser.objects.get(username=request.session['username'])
            # Timestamp has expired
            if user.expires_timestamp < timezone.now():
                if not request.GET.get('code'):
                    return render(request, '/login')
                    # Update the user object info
                user = create_user(request.GET.get('code'), request)
        except ApiUser.DoesNotExist:
            if not request.GET.get('code'):
                return render(request, '/login')
            # Create a new user
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
        patients_url = data['next']  # A JSON null on the last page

    # json_string = u'{ "id":"123456789", ... }'
    # obj = json.loads(json_string)    # obj now contains a dict of the data
    #
    # converted  = json.loads(u' + patients[0])
    # #print converted[0]

    context = {
        'title': 'API Home',
        'patientsinfo': patients[0],
    }

    return render(request, "api.html", context)
