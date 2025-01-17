# =============================================================================
# codePost v2.0 SDK
#
# ASSIGNMENT MODEL SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import typing as _typing

# Local imports
from . import abstract as _abstract

# =============================================================================

class Courses(
    _abstract.APIResource,
    _abstract.ReadableAPIResource,
    _abstract.UpdatableAPIResource,
    metaclass=_abstract.APIResourceMetaclass
):
    _OBJECT_NAME = "courses"
    _FIELD_ID = "id"
    _FIELDS = {
        "name":                         (str, "The course's name (e.g. 'CS 101')."),
        "period":                       (str, "The course's period (e.g. 'Fall 2019'). This field allows you to create multiple objects which represent instances of the same course over different periods (e.g. every semester)."),
        "assignments":                  (_typing.List, "IDs of the Assignments in this course."),
        "sections":                     (_typing.List, "IDs of the Sections in this course."),
        "sendReleasedSubmissionsToBack":(bool, "A course setting. If True, submissions released by graders will be sent to the back of the grading queue. This ensures that released submissions will be re-claimed only after all other Submissions have been claimed."),
        "showStudentsStatistics":       (bool, "A course setting. If True, students will be able to view the Mean and Median of this Course's published Assignments."),
        "timezone":                     (str, "A course setting. Must be a valid pytz timezone."),
        "emailNewUsers":                (bool, "A course setting. If True, users of any role added to this Course's roster will be sent a notification email."),
        "anonymousGradingDefault":      (bool, "A course setting. If True, newly created assignments will automatically be set to Anonymous Grading Mode."),
        "allowGradersToEditRubric":     (bool, "A course setting. If True, graders and course admins will be able to edit an Assignment's directly rubric from the Code Review console."),
    }
    _FIELDS_READ_ONLY = [ ]
    _FIELDS_REQUIRED = [ "name", "period" ]

    def list_available(self, name=None, period=None):
        """
        Returns the list of all courses that the authenticated user (as
        identified by the API key) has administrative access to.

        Optionally, it is possible to filter courses according to their `name`
        and/or `period`.

        If you are unable to retrieve a course that you should have access to,
        you may either not be using the right API key, or you may not have
        properly set the API key, i.e.,
            `codepost.configure_api_key(api_key=...)`
        """
        _class_type = type(self)

        ret = self._requestor._request(
            endpoint=self.class_endpoint,
            method="GET",
        )
        
        if ret.status_code == 200:
            # Returns a list of courses
            course_list = list(map(lambda kws: _class_type(**kws), ret.json))

            # Optionally filter according to the `name` parameter
            if name:
                course_list = filter(lambda c: c.name == name, course_list)

            # Optionally filter according to the `period` parameter
            if period:
                course_list = filter(lambda c: c.period == period, course_list)
            
            return course_list
        
        return []

# =============================================================================
