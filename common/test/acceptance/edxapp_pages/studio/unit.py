"""
Unit page in Studio
"""

from bok_choy.page_object import PageObject


class UnitPage(PageObject):
    """
    Unit page in Studio
    """

    @property
    def name(self):
        return "studio.unit"

    def url(self):
        raise NotImplementedError

    def is_browser_on_page(self):
        return self.is_css_present('body.view-unit')
