from django.shortcuts import render
from .forms import SignUpForm, ContactForm
import datetime, pytz, requests
import json
from .models import ApiUser


# Create your views here.
def home(request):
    title = "title for the page for user %s" % (request.user)

    form = SignUpForm(request.POST or None)

    context = {
        "title": title,
        "form": form,
    }

    if form.is_valid():
        # print request.POST['email']
        instance = form.save(commit=False)
        # full_name=form.cleaned_data.get("full_name")
        instance.save()

        context = {
            "title": "Thanks for submitting, guy"
        }

    return render(request, "home.html", context)


def contact(request):
    form = ContactForm(request.POST or None)

    passed_email = ''
    cleaned_data = ''

    if form.is_valid():
        # In "theory", an email could be sent here, but, meh
        passed_email = form.cleaned_data.get("dat_email_doh")

        cleaned_data = form.cleaned_data

        for key in form.cleaned_data:
            print key
            print form.cleaned_data.get(key)

    context = {
        "title": "Contact form title lyfe",
        "form": form,
        "passed": passed_email,
        "cleaned": cleaned_data,
    }

    return render(request, "contact.html", context)


def create_user_object(code, request):
    response = requests.post('https://drchrono.com/o/token/', data={
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8000/api/',
        'client_id': 'kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa',
        'client_secret': '8DWCWZP2YuOXONuIkTetaNHjF2nfyLmDCrbJFomGKrMJyyjJiGSdDS0rANiukFZ5Y4HSricrKLOEqEZFFMP017u6bbxVE06BE8X5EEN0Y0XKMP9ggp7ZHaCwrrD9Ecv5',
    })
    response.raise_for_status()
    data = response.json()

    user = ApiUser(username=request.session['username'], access_token=data['access_token'],
                   refresh_token=data['refresh_token'],
                   expires_timestamp=datetime.datetime.now(pytz.utc) + datetime.timedelta(
                       seconds=data['expires_in']))

    return user


def api(request):
    from django.utils import timezone

    request.session['username'] = 'alex'

    # Check to see if a user with the session username exists
    try:
        user = ApiUser.objects.get(username=request.session['username'])
        # Timestamp has expired
        if user.expires_timestamp < timezone.now():
            # TODO: check to see if 'code' is set in GET request

            # Update the user object info
            user = create_user_object(request.GET.get('code'), request)
            user.save()
    except ApiUser.DoesNotExist:

        # TODO: check to see if 'code' is set in GET request


        # Create a new user
        user = create_user_object(request.GET.get('code'), request)
        user.save()

    # User info
    response = requests.get('https://drchrono.com/api/users/current', headers={
        'Authorization': 'Bearer %s' % user.access_token,
    })
    response.raise_for_status()
    userinfo = response.json()

    # username = data['username']

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
        "userinfo": userinfo,
        "patientsinfo": patients[0],
    }

    return render(request, "api.html", context)
