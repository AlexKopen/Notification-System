from django.shortcuts import render
from .forms import SignUpForm, ContactForm


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
