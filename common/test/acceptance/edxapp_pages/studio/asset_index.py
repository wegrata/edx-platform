"""
The Files and Uploads page for a course in Studio
"""

from bok_choy.page_object import PageObject
from .helpers import parse_course_id
from . import BASE_URL


class AssetIndexPage(PageObject):
    """
    The Files and Uploads page for a course in Studio
    """

    @property
    def name(self):
        return "studio.uploads"

    def url(self, course_id=None):  #pylint: disable=W0221
        """
        URL to the files and uploads page for a course.
        `course_id` is a string of the form "org.number.run", and it is required
        """
        _, _, course_run = parse_course_id(course_id)

        return "{0}/assets/{1}/branch/draft/block/{2}".format(
            BASE_URL, course_id, course_run
        )

    def is_browser_on_page(self):
        return self.is_css_present('body.view-uploads')
