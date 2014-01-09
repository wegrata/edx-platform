"""
My Courses page in Studio
"""

from bok_choy.page_object import PageObject
from . import BASE_URL


class DashboardPage(PageObject):
    """
    My Courses page in Studio
    """

    @property
    def name(self):
        return "studio.dashboard"

    def url(self):
        return BASE_URL + "/course"

    def is_browser_on_page(self):
        return self.is_css_present('body.view-dashboard')
