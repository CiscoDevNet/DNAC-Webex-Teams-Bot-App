"""
Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
import re

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

"""
This file is a utility file for performing various helper function
"""

def join_url(url, *paths):
    """
    Joins individual URL strings together, and returns a single string.
    Usage::
        >>> util.join_url("cisco.com", "dnac.html")
        'cisco.com/dnac.html'
    """
    for path in paths:
        url = re.sub(r'/?$', re.sub(r'^/?', '/', path), url)
    return url


def join_header(data, *override):
    """
    Merges any number of dictionaries together, and returns a single dictionary
    Usage::
        >>> util.join_header ({"a": "b"}, {"dnac": "cisco"})
        {'a': 'b', 'dnac': 'cisco'}
    """
    result = {}
    for current_dict in (data,) + override:
        result.update(current_dict)
    return result