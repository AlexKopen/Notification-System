from django.shortcuts import render
from .forms import SignUpForm


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
