from django.shortcuts import render


# Create your views here.
def home(request):
    title = "title for the page for user %s" %(request.user)
    context = {
        "title": title,
    }
    return render(request, "home.html", context)
