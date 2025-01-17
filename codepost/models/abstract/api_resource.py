# =============================================================================
# codePost v2.0 SDK
#
# API RESOURCE SUB-MODULE
# =============================================================================

from __future__ import print_function # Python 2

# Python stdlib imports
import copy as _copy
import functools as _functools
import inspect as _inspect
import json as _json
import logging as _logging
import os as _os
import platform as _platform
import threading as _threading
import time as _time
import uuid as _uuid
import sys as _sys
try:
    # Python 3
    from urllib.parse import urljoin
    from urllib.parse import quote as urlquote
    from urllib.parse import urlencode as urlencode
except ImportError: # pragma: no cover
    # Python 2
    from urlparse import urljoin
    from urllib import quote as urlquote
    from urllib import urlencode as urlencode

# External dependencies
import better_exceptions as _better_exceptions
import requests as _requests

# Local imports
import codepost
import codepost.api_requestor as _api_requestor
import codepost.errors as _errors
import codepost.util.logging as _logging
import codepost.util.misc as _misc

# =============================================================================

# Global submodule constants
_LOG_SCOPE = "{}".format(__name__)

# Global submodule protected attributes
_logger = _logging.get_logger(name=_LOG_SCOPE)

# =============================================================================

class AbstractAPIResource(object):
    """
    Abstract class type for a codePost API resource.
    """

    _data = dict()
    _requestor = _api_requestor.STATIC_REQUESTOR
    
    def _get_id(self, id=None):
        raise NotImplementedError("abstract class not meant to be used")
    
    def _get_data_and_extend(self, **kwargs):
        raise NotImplementedError("abstract class not meant to be used")
    
    def _validate_data(self, data, required=True):
        raise NotImplementedError("abstract class not meant to be used")

    @property
    def class_endpoint(self):
        raise NotImplementedError("abstract class not meant to be used")
    
    @property
    def instance_endpoint(self):
        raise NotImplementedError("abstract class not meant to be used")
    
    def instance_endpoint_by_id(self, id=None):
        raise NotImplementedError("abstract class not meant to be used")

# =============================================================================

class APIResource(AbstractAPIResource):
    """
    Base class type to store and manipulate a codePost API resource.
    """

    # Class constants
    _FIELD_ID = "id"

    # Class attributes
    _data = None
    _field_names = None
    _static = False

    def __init__(self, requestor=None, static=False, **kwargs):

        # Initialize requestor
        self._requestor = requestor
        if not isinstance(self._requestor, _api_requestor.APIRequestor):
            self._requestor = _api_requestor.STATIC_REQUESTOR
        
        # Initialize dictionary fields
        _fields = getattr(self, "_FIELDS", list())
        if isinstance(_fields, dict):
            _fields = dict(_fields)
            _fields = list(_fields.keys())
        if getattr(self, "_FIELD_ID", ""):
            _fields.append(self._FIELD_ID)
        self._field_names = _fields
        
        self._static = static

        if not self._static:
            self._data = getattr(self, "_data", dict())
            if not self._data:
                self._data = dict()
        
        for key in kwargs.keys():
            if key in self._field_names:
                self._data[key] = kwargs[key]
    
    def _get_id(self, id=None):
        if id == None:
            if self._static:
                raise _errors.StaticObjectError()
            
            data = getattr(self, "_data", None)
            if isinstance(data, dict) and "id" in data and data["id"]:
                id = data["id"]
        
        return id
    
    def _validate_data(self, data, required=True):
        return True
    
    def  __getstate__(self):
        state = dict(self.__dict__)
        if "_requestor" in state:
            # This class cannot be pickled for the moment
            del state["_requestor"]
        return state
    
    def __setstate__(self, state):
        self.__dict__ = state
        if self.__dict__.get("requestor", None) is None:
            self.__dict__["requestor"] = _api_requestor.STATIC_REQUESTOR
        return self

    def _get_data_and_extend(self, **kwargs):
        data = dict()
        
        # If this is a static object, we should ignore self._data

        if not self._static and isinstance(self._data, dict):
            # Combine instance data and extended (typically kwargs) argument
            data.update(_copy.deepcopy(self._data))

        if kwargs:
            # Make sure not to erase fields

            # NOTE: In a more controled and documented manner, field erasure
            # could be a feature.

            kwargs_copy = {
                key: _copy.deepcopy(value)
                for (key, value) in kwargs.items()
                if _misc.is_field_set_in_kwargs(key, kwargs)
            }

            data.update(kwargs_copy)
        
        # Remove extraneous (unexpected) data + blank fields
        
        new_data = {
            key : data[key]
            for key in data.keys()
            if (key in self._field_names) and (data[key] != None)
        }
        
        return new_data

    @property
    def class_endpoint(self):
        classname = getattr(self, "_OBJECT_NAME", "")
        if classname:
            classname = classname.replace("..", "/{}/")
            classname = classname.replace(".", "/")
            endpoint = "/{}/".format(classname)
            return endpoint
    
    def instance_endpoint_by_id(self, id=None):
        if id == None and getattr(self, "_data", None):
            id = self._data.get("id", None)
        if id:
            try:
                tmp = self.class_endpoint.format(id)
                if tmp != self.class_endpoint:
                    return tmp
            except IndexError: # means formatting didn't work
                pass
            return urljoin(self.class_endpoint, str(id))
    
    @property
    def instance_endpoint(self):
        if getattr(self, "_data", None):
            return self.instance_endpoint_by_id(id=self._data.get("id"))
           
    def _request(self, **kwargs):
        self._requestor._request(**kwargs)
    
    def __repr__(self):
        if getattr(self, "_data", None):
            return self._data.__repr__()
        return dict().__repr__()

# =============================================================================
