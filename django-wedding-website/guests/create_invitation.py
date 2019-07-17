from __future__ import unicode_literals
from copy import copy
from email.mime.image import MIMEImage
import os
from datetime import datetime
import random

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from guests.models import Party


INVITATION_TEMPLATE = 'guests/email_templates/final_invitation.html'
INVITATION_CONTEXT_MAP = {
        # 'lions-head': {
        #     'title': "Taiwan Forest",
        #     'header_filename': 'hearts.png',
        #     'main_image': 'taiwan_forest_rot.png',
        #     'main_color': '#fff3e8',
        #     'font_color': '#666666',
        # },
        'invitation': {
            'title': "Invitation",
            'header_filename': 'hearts.png',
            'main_image': 'engaement.png',
            'main_color': '#2aabd2',
            'font_color': '#ffffff',
        },
        # 'ski-trip': {
        #     'title': 'Ski Trip',
        #     'header_filename': 'hearts.png',
        #     'main_image': 'ski-trip.jpg',
        #     'main_color': '#330033',
        #     'font_color': '#ffffff',
        # },
        # 'canada': {
        #     'title': 'Canada!',
        #     'header_filename': 'maple-leaf.png',
        #     'main_image': 'canada-cartoon-resized.jpg',
        #     'main_color': '#ea2e2e',
        #     'font_color': '#e5ddd9',
        # },
        # 'american-gothic': {
        #     'title': 'American Gothic',
        #     'header_filename': 'hearts.png',
        #     'main_image': 'american-gothic.jpg',
        #     'main_color': '#b6ccb5',
        #     'font_color': '#000000',
        # },
        # 'plunge': {
        #     'title': 'The Plunge',
        #     'header_filename': 'plunger.png',
        #     'main_image': 'plunge.jpg',
        #     'main_color': '#b4e6ff',
        #     'font_color': '#000000',
        # },
        # 'dimagi': {
        #     'title': 'Dimagi',
        #     'header_filename': 'commcare.png',
        #     'main_image': 'join-us.jpg',
        #     'main_color': '#003d71',
        #     'font_color': '#d6d6d4',
        # }
    }


def send_all_save_the_dates(test_only=False, mark_as_sent=False):
    to_send_to = Party.in_default_order().filter(is_invited=True, save_the_date_sent=None)
    for party in to_send_to:
        send_save_the_date_to_party(party, test_only=test_only)
        if mark_as_sent:
            party.save_the_date_sent = datetime.now()
            party.save()


def send_save_the_date_to_party(party, test_only=False):
    context = get_save_the_date_context(get_template_id_from_party(party))
    recipients = party.guest_emails
    if not recipients:
        print '===== WARNING: no valid email addresses found for {} ====='.format(party)
    else:
        send_save_the_date_email(
            context,
            recipients,
            test_only=test_only
        )


def get_template_id_from_party(party):
    if party.type == 'formal':
        # all formal guests get formal invites
        return random.choice(['lions-head', 'ski-trip'])
    elif party.type == 'dimagi':
        # all non-formal dimagis get dimagi invites
        return 'dimagi'
    elif party.type == 'fun':
        all_options = SAVE_THE_DATE_CONTEXT_MAP.keys()
        all_options.remove('dimagi')
        if party.category == 'ro':
            # don't send the canada invitation to ro's crowd
            all_options.remove('canada')
        # otherwise choose randomly from all options for everyone else
        return random.choice(all_options)
    else:
        return None


def get_invitation_context(template_id, recipient=None):
    template_id = (template_id or '').lower()
    if template_id not in INVITATION_CONTEXT_MAP:
        template_id = 'lions-head'
    context = copy(INVITATION_CONTEXT_MAP[template_id])
    context['name'] = template_id
    context['page_title'] = 'Invitation to Our Wedding!'
    context['preheader_text'] = (
        "The date that you've eagerly been waiting for is finally here. "
        "Connor and Fiona are getting married! Save the date!"
    )
    context['recipient'] = recipient
    return context


def invitation_email(context, recipients, test_only=False):
    context['email_mode'] = True
    context['rsvp_address'] = settings.DEFAULT_WEDDING_REPLY_EMAIL
    template_html = render_to_string(SAVE_THE_DATE_TEMPLATE, context=context)
    template_text = "We are happy to invite to our wedding! The date is September 8, 2019" \
                    " from 4pm to 11pm at the LBJ Wildflower Center." \
                    "Please click to RSVP!"
    subject = 'Save the Date!'
    # https://www.vlent.nl/weblog/2014/01/15/sending-emails-with-embedded-images-in-django/
    msg = EmailMultiAlternatives(subject, template_text, settings.DEFAULT_WEDDING_FROM_EMAIL, recipients,
                                 reply_to=[settings.DEFAULT_WEDDING_REPLY_EMAIL])
    msg.attach_alternative(template_html, "text/html")
    msg.mixed_subtype = 'related'
    for filename in (context['header_filename'], context['main_image']):
        attachment_path = os.path.join(os.path.dirname(__file__), 'static', 'save-the-date', 'images', filename)
        with open(attachment_path, "rb") as image_file:
            msg_img = MIMEImage(image_file.read())
            msg_img.add_header('Content-ID', '<{}>'.format(filename))
            msg.attach(msg_img)

    print 'sending {} to {}'.format(context['name'], ', '.join(recipients))
    if not test_only:
        msg.send()


def clear_all_save_the_dates():
    for party in Party.objects.exclude(save_the_date_sent=None):
        party.save_the_date_sent = None
        party.save()
