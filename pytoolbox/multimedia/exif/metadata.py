# -*- encoding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

from pytoolbox import exceptions, module
from pytoolbox.encoding import string_types

from . import camera, image, lens, photo, tag

_all = module.All(globals())


class Metadata(object):

    camera_class = camera.Camera
    image_class = image.Image
    lens_class = lens.Lens
    photo_class = photo.Photo
    tag_class = tag.Tag

    def __init__(self, path=None, buf=None, orientation=None, gexiv2_version='0.10'):
        import gi
        gi.require_version('GExiv2', gexiv2_version)
        from gi.repository import GExiv2
        self.path = path
        self.exiv2 = GExiv2.Metadata()
        if buf:
            self.exiv2.open_buf(buf)
        elif path:
            self.exiv2.open_path(path)
        else:
            raise ValueError('buf or file is required')
        self.camera = self.camera_class(self)
        self.image = self.image_class(self, orientation)
        self.lens = self.lens_class(self)
        self.photo = self.photo_class(self)

    def __getitem__(self, key):
        # FIXME make it more strict and re-implement less strict self.get(key)
        return self.tag_class(self, key)

    def __setitem__(self, key, value):
        self.exiv2[key] = value

    @property
    def tags(self):
        return {k: self[k] for k in self.exiv2.get_tags()}

    def get_date(self, keys=('Exif.Photo.DateTimeOriginal', 'Exif.Image.DateTime'), fail=True):
        for key in ([keys] if isinstance(keys, string_types) else keys):
            date = self[key].data
            if isinstance(date, datetime.datetime):
                return date

    def rewrite(self, path=None, save=False):
        """
        Iterate over all tags and rewrite them to fix issues (e.g. GExiv2: Invalid ifdId 103 (23)).
        """
        tags = {k: str(v.data) for k, v in self.tags.iteritems()}
        self.exiv2.clear()
        for key, value in tags.iteritems():
            self[key] = value
        if save:
            self.save_file(path=path)

    def save_file(self, path=None):
        if not path and not self.path:
            raise exceptions.UndefinedPathError()
        return self.exiv2.save_file(path=path or self.path)


__all__ = _all.diff(globals())
