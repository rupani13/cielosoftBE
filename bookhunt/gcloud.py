"""
Modify django-storages for GCloud to set static, media folder in a bucket
"""
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage


class GoogleCloudMediaStorage(GoogleCloudStorage):
    """
    GoogleCloudStorage suitable for Django's Media files.
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = 'media'
        super(GoogleCloudMediaStorage, self).__init__(*args, **kwargs)


class GoogleCloudStaticStorage(GoogleCloudStorage):
    """
    GoogleCloudStorage suitable for Django's Static files
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = 'static'
        super(GoogleCloudStaticStorage, self).__init__(*args, **kwargs)

# from django.conf import settings
# from storages.backends.gcloud import GoogleCloudStorage
# from storages.utils import setting
# from urllib.parse import urljoin
# class GoogleCloudMediaFileStorage(GoogleCloudStorage):
#     """
#     Google file storage class which gives a media file path from       MEDIA_URL not google generated one.
#     """
#     bucket_name = setting('GS_BUCKET_NAME')
#     def url(self, name):
#         """
#         Gives correct MEDIA_URL and not google generated url.
#         """
#         return urljoin(settings.MEDIA_URL, name)