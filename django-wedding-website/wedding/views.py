from django.conf import settings
from django.shortcuts import render
from guests.save_the_date import SAVE_THE_DATE_CONTEXT_MAP
from django.shortcuts import redirect


def home(request):
    a = 5
    test = settings.BASE_DIR
    return render(request, 'home.html', context={
        'save_the_dates': SAVE_THE_DATE_CONTEXT_MAP,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
    })


def RSVP(request):
    return redirect("https://docs.google.com/forms/d/e/1FAIpQLSceuRSKtxlTz_fX4PbDnHvt-XBWPugy42Z8GWeIYfTlZnc5rA/viewform?usp=sf_link")
