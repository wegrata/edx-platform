"""
Course navigation page object
"""

import re
from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise, fulfill_after


class CourseNavPage(PageObject):
    """
    Navigate sections and sequences in the courseware.
    """

    @property
    def name(self):
        return "lms.course_nav"

    def url(self, **kwargs):
        """
        Since course navigation appears on multiple pages,
        it doesn't have a particular URL.
        """
        raise NotImplementedError

    def is_browser_on_page(self):
        return self.is_css_present('section.course-index')

    @property
    def sections(self):
        """
        Return a dictionary representation of sections and subsections.

        Example:

            {
                'Introduction': ['Course Overview'],
                'Week 1': ['Lesson 1', 'Lesson 2', 'Homework']
                'Final Exam': ['Final Exam']
            }

        You can use these titles in `go_to_section` to navigate to the section.
        """
        # Dict to store the result
        nav_dict = dict()

        section_titles = self._section_titles()

        # Get the section titles for each chapter
        for sec_index in range(len(section_titles)):

            sec_title = section_titles[sec_index]

            if len(section_titles) < 1:
                self.warning("Could not find subsections for '{0}'".format(sec_title))
            else:
                # Add one to convert list index (starts at 0) to CSS index (starts at 1)
                nav_dict[sec_title] = self._subsection_titles(sec_index + 1)

        return nav_dict

    @property
    def sequence_items(self):
        """
        Return a list of sequence items on the page.
        Sequence items are one level below subsections in the course nav.

        Example return value:
            ['Chemical Bonds Video', 'Practice Problems', 'Homework']
        """
        seq_css = 'ol#sequence-list>li>a>p'
        return self.css_map(seq_css, self._clean_seq_titles)

    def go_to_section(self, section_title, subsection_title):
        """
        Go to the section in the courseware.
        Every section must have at least one subsection, so specify
        both the section and subsection title.

        Example:
            go_to_section("Week 1", "Lesson 1")
        """

        # For test stability, disable JQuery animations (opening / closing menus)
        self.disable_jquery_animations()

        # Get the section by index
        try:
            sec_index = self._section_titles().index(section_title)
        except ValueError:
            self.warning("Could not find section '{0}'".format(section_title))
            return

        # Click the section to ensure it's open (no harm in clicking twice if it's already open)
        # Add one to convert from list index to CSS index
        section_css = 'nav>div.chapter:nth-of-type({0})>h3>a'.format(sec_index + 1)
        self.css_click(section_css)

        # Get the subsection by index
        try:
            subsec_index = self._subsection_titles(sec_index + 1).index(subsection_title)
        except ValueError:
            msg = "Could not find subsection '{0}' in section '{1}'".format(subsection_title, section_title)
            self.warning(msg)
            return

        # Convert list indices (start at zero) to CSS indices (start at 1)
        subsection_css = "nav>div.chapter:nth-of-type({0})>ul>li:nth-of-type({1})>a".format(
            sec_index + 1, subsec_index + 1
        )

        # Click the subsection and ensure that the page finishes reloading
        with fulfill_after(self._on_section_promise(section_title, subsection_title)):
            self.css_click(subsection_css)

    def go_to_sequential(self, sequential_title):
        """
        Within a section/subsection, navigate to the sequential with `sequential_title`.
        """

        # Get the index of the item in the sequence
        all_items = self.sequence_items

        try:
            seq_index = all_items.index(sequential_title)

        except ValueError:
            msg = "Could not find sequential '{0}'.  Available sequentials: [{1}]".format(
                sequential_title, ", ".join(all_items)
            )
            self.warning(msg)

        else:

            # Click on the sequence item at the correct index
            # Convert the list index (starts at 0) to a CSS index (starts at 1)
            seq_css = "ol#sequence-list>li:nth-of-type({0})>a".format(seq_index + 1)
            self.css_click(seq_css)

    def _section_titles(self):
        """
        Return a list of all section titles on the page.
        """
        chapter_css = 'nav>div.chapter>h3>a'
        return self.css_map(chapter_css, lambda el: el.text.strip())

    def _subsection_titles(self, section_index):
        """
        Return a list of all subsection titles on the page
        for the section at index `section_index` (starts at 1).
        """
        # Retrieve the subsection title for the section
        # Add one to the list index to get the CSS index, which starts at one
        subsection_css = 'nav>div.chapter:nth-of-type({0})>ul>li>a>p:nth-of-type(1)'.format(section_index)

        # If the element is visible, we can get its text directly
        # Otherwise, we need to get the HTML
        # It *would* make sense to always get the HTML, but unfortunately
        # the open tab has some child <span> tags that we don't want.
        return self.css_map(
            subsection_css,
            lambda el: el.text.strip().split('\n')[0] if el.visible else el.html.strip()
        )

    def _on_section_promise(self, section_title, subsection_title):
        """
        Return a `Promise` that is fulfilled when the user is on
        the correct section and subsection.
        """
        desc = "currently at section '{0}' and subsection '{1}'".format(section_title, subsection_title)
        return EmptyPromise(
            lambda: self._is_on_section(section_title, subsection_title), desc
        )

    def _is_on_section(self, section_title, subsection_title):
        """
        Return a boolean indicating whether the user is on the section and subsection
        with the specified titles.

        This assumes that the currently expanded section is the one we're on
        That's true right after we click the section/subsection, but not true in general
        (the user could go to a section, then expand another tab).
        """
        current_section_list = self.css_text('nav>div.chapter.is-open>h3>a')
        current_subsection_list = self.css_text('nav>div.chapter.is-open li.active>a>p')

        if len(current_section_list) == 0:
            self.warning("Could not find the current section")
            return False

        elif len(current_subsection_list) == 0:
            self.warning("Could not find current subsection")
            return False

        else:
            return (
                current_section_list[0].strip() == section_title and
                current_subsection_list[0].strip().split('\n')[0] == subsection_title
            )

    # Regular expression to remove HTML span tags from a string
    REMOVE_SPAN_TAG_RE = re.compile(r'<span.+/span>')

    def _clean_seq_titles(self, element):
        """
        Clean HTML of sequence titles, stripping out span tags and returning the first line.
        """
        return self.REMOVE_SPAN_TAG_RE.sub('', element.html).strip().split('\n')[0]
