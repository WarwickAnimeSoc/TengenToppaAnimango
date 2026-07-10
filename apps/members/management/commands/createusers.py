import logging
import requests
from smtplib import SMTPAuthenticationError

# Attempt to use cElementTree instead of ElementTree if possible, as it's faster and uses less memory.
# Credit to Sorc
try:
    from xml.etree.cElementTree import ElementTree, Element, fromstring
except ImportError:
    from xml.etree.ElementTree import ElementTree, Element, fromstring

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.defaultfilters import title
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail


class SUMember:
    warwick_id: str
    first_name: str
    last_name: str
    email: str

    def __init__(self, xml_member: Element):
        warwick_id = xml_member.find('UniqueID')
        first_name = xml_member.find('FirstName')
        last_name = xml_member.find('LastName')
        email = xml_member.find('EmailAddress')

        # IDK what the previous version was trying to do, because it would just silently fails.
        # TODO: check SU API to see if such case would actually happen
        if warwick_id is None or warwick_id.text is None:
            raise ValueError("A non-student has joined the society")


        if ((warwick_id is None or warwick_id.text is None) or
            (first_name is None or first_name.text is None) or 
            (last_name is None or last_name.text is None) or
            (email is None or email.text is None)):
            raise ValueError("Required fields not found. SU API may have changed.")

        # Student ID validation
        if len(warwick_id.text) != 7:
            raise ValueError('Warwick IDs should be a 7 digit integer! {0!s} is not valid'.format(warwick_id))

        try:
            int(warwick_id.text)
        except ValueError:
            raise ValueError('Warwick IDs should be a 7 digit integer! {0!s} is not valid'.format(warwick_id))

        self.warwick_id = warwick_id.text
        self.first_name = title(first_name.text)
        self.last_name = title(last_name.text)
        self.email = email.text


def get_members() -> list[SUMember]:
    # Get#'s a list of all the current members from the SU API.
    try:
        request = requests.get('https://www.warwicksu.com/membershipapi/listmembers/' + settings.SU_API_KEY)
    except Exception as e:
        raise e

    # API response is in xml.
    xml_tree = fromstring(request.text.encode('utf-8'))
    members = []
    for xml_member in xml_tree:
        members.append(SUMember(xml_member))

    return members


def remove_existing_members(members_list: list[SUMember]) -> list[SUMember]:
    # Prunes members who already have an account from a list of members.
    new_members = []
    for member in members_list:
        if not User.objects.filter(username=member.warwick_id).exists():
            new_members.append(member)

    return new_members


def send_signup_mail(user: User, password: str) -> None:
    subject = 'Welcome to the University of Warwick Anime and Manga Society'
    message = 'Hi,\n\n' \
              'Welcome to the University of Warwick Anime and Manga Society! Your login details are as follows:\n\n' \
              'Username: {username}\n' \
              'Password: {password}\n\n' \
              'You can log in at https://animesoc.co.uk/members/login/. We suggest you change your \n' \
              'password as soon as you log in. Do that by clicking on your temporary nickname (top right corner)\n' \
              'and then selecting profile. Don\'t forget to change your nickname, too!\n\n' \
              'Regards,\n' \
              'Warwick Anime and Manga Society\n\n'.format(username=user.username, password=password)
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def create_new_members(members_list: list[SUMember], logger: logging.Logger) -> None:
    # Every member in members_list should be valid at this point.
    for member in members_list:
        temporary_password = get_random_string(12)

        # Try to create the new User object.
        try:
            user = User.objects.create_user(
                username=member.warwick_id,
                password=temporary_password,
                email=member.email,
                first_name=member.first_name,
                last_name=member.last_name
            )
            user.save()
        except ValueError:
            # Need this to skip past Chih's account.
            continue
        except Exception as e:
            raise e

        # Try to send an email to the new user containing their temporary password.
        try:
            send_signup_mail(user, temporary_password)
        except SMTPAuthenticationError:
            # Delete the user if the email fails to send
            user.delete()

            error_string = 'There was an error connecting to the society gmail. Check the less secure devices setting' \
                           ' in gmail.'
            raise PermissionError(error_string)
        except Exception as e:
            # Delete the user if the email fails to send
            user.delete()
            raise e

        # If no errors then log the user as created
        logger.info('Created user: {0!s} {1!s} ({2!s}) | Welcome email has been sent to {3!s}'.format(
            member.first_name, member.last_name, member.warwick_id, member.email
        ))


class Command(BaseCommand):
    help = 'Gets a list of all current members from the SU and creates accounts for them'

    def handle(self, *args, **options):
        logger = logging.getLogger('user_creator_logger')

        try:
            members_list = get_members()
            new_members = remove_existing_members(members_list)
            logger.info(
                'Synced with SU. Total members: {0!s} | New members: {1!s}'.format(len(members_list), len(new_members)))

            if new_members:
                create_new_members(new_members, logger)
                pass
            print('[SUCCESS] Created {0!s} new members!'.format(len(new_members)))  # For discord bot
        except Exception as e:
            print('[ERROR] {0!s}'.format(e))   # For discord bot
            logger.exception(e)
