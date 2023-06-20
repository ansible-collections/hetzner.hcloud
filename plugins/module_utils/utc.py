from __future__ import absolute_import, division, print_function

__metaclass__ = type

from datetime import timedelta, tzinfo

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class UTC(tzinfo):
    """Custom UTC for compatibility with Python 2.7"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
