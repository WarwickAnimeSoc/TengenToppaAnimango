import re
import requests
import json

from django.core.exceptions import ValidationError


# The anilist_api file is now stored in the showings app. There's no real reason for this other than that I would like
# to keep the root directory clear of anything that isn't an app for the site.


def populate_series_item(series_object):
    # The admin form for Series should already have validated that the anilist_url field matches the correct
    # format for an anilist link. The link could still be invalid, but the format must be correct.
    url_values = re.split(r'/', re.sub(r'(https://)*(www\.)*(anilist.co/)*', '', str(series_object.anilist_link)))
    api_id = url_values[1]
    try:
        api_response_json = api_get_info(api_id)
    except Exception as e:
        raise ValidationError(repr(e))

    # Populate fields using api response.
    series_object.title_romaji = api_response_json['title']['romaji']
    series_object.api_id = int(api_response_json['id'])
    # Anilist api returns series_type in all caps. This doesn't cause issues with anilist links as they aren't case
    # sensitive. However, MAL is case sensitive and requires the media type to be lowercase, so it's better to set it
    # to lower case at this point.
    series_object.series_type = api_response_json['type'].lower()
    series_object.synopsis = api_response_json['description']
    series_object.cover_link = api_response_json['coverImage']['large']
    # Reformat the anilist_link to remove the title as it is unnecessary but is likely to be present if the url was
    # copied from a browser. E.G https://anilist.co/anime/19111/Love-Live-School-idol-project-2nd-Season/ is replaced
    # by the shorter https://anilist.co/anime/19111/
    series_object.anilist_link = 'https://anilist.co/{0!s}/{1!s}'.format(series_object.series_type,
                                                                         str(series_object.api_id))

    # English titles are not always available so check before settings.
    if api_response_json['title']['english'] is not None:
        series_object.title_english = api_response_json['title']['english']

    # Most anilist shows also store the MAL id so we can also populate the Mal URl.
    if api_response_json['idMal'] is not None:
        series_object.mal_link = 'https://myanimelist.net/{0!s}/{1!s}'.format(series_object.series_type,
                                                                              str(api_response_json['idMal']))


def api_get_info(api_id):
    # Uses the anilist v2 api
    # https://github.com/AniList/ApiV2-GraphQL-Docs
    query = '''
    query ($id: Int) { 
      Media (id: $id) { 
        id
        idMal
        title {
            romaji
            english
        }
        type
        description
        coverImage {
            large
        }
      }
    }
    '''
    query_variables = {'id': api_id}
    api_url = 'https://graphql.anilist.co'

    api_response = requests.post(api_url, json={'query': query, 'variables': query_variables})

    # If the link was invalid, the next line will raise an error as Media will not be a key in the response
    return json.loads(api_response.content.decode("utf-8"))['data']['Media']
