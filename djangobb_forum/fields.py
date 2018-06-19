from django.utils import six

try:
    from cStringIO import StringIO
except ImportError:
    StringIO = six.StringIO
import random
from hashlib import sha1

from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from annoying.fields import AutoOneToOneField


class ExtendedImageField(models.ImageField):
    """
    Extended ImageField that can resize image before saving it.
    """

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        super(ExtendedImageField, self).__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if data and self.width and self.height:
            content = self.resize_image(data.read(), width=self.width, height=self.height)
            salt = sha1(str(random.random())).hexdigest()[:5]
            fname = sha1(salt + settings.SECRET_KEY).hexdigest() + '.png'
            data = SimpleUploadedFile(fname, content, content_type='image/png')
        super(ExtendedImageField, self).save_form_data(instance, data)

    def resize_image(self, rawdata, width, height):
        """
        Resize image to fit it into (width, height) box.
        """
        try:
            import Image
        except ImportError:
            from PIL import Image
        image = Image.open(StringIO(rawdata))
        oldw, oldh = image.size
        if oldw >= oldh:
            x = int(round((oldw - oldh) / 2.0))
            image = image.crop((x, 0, (x + oldh) - 1, oldh - 1))
        else:
            y = int(round((oldh - oldw) / 2.0))
            image = image.crop((0, y, oldw - 1, (y + oldw) - 1))
        image = image.resize((width, height), resample=Image.ANTIALIAS)

        string = StringIO()
        image.save(string, format='PNG')
        return string.getvalue()


# class JSONField(six.with_metaclass(models., models.TextField)):
#     """
#     JSONField is a generic textfield that neatly serializes/unserializes
#     JSON objects seamlessly.
#     Django snippet #1478
#     """
#
#     # __metaclass__ = models.SubfieldBase
#
#     def to_python(self, value):
#         if value == "":
#             return None
#
#         try:
#             if isinstance(value, six.string_types):
#                 return json.loads(value)
#         except ValueError:
#             pass
#         return value
#
#     def get_prep_value(self, value):
#         if value == "":
#             return None
#         if isinstance(value, dict):
#             value = json.dumps(value, cls=DjangoJSONEncoder)
#         return super(JSONField, self).get_prep_value(value)


__ALL__ = [JSONField, AutoOneToOneField, DjangoJSONEncoder]
