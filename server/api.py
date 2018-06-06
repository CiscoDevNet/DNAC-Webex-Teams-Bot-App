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

import json
import requests
import util as util
import datetime
import logging

"""
This file contains the boiler plate code to login , make API requests- GET , POST , PUT , DELETE
The API Object contains the IP(Endpoint) , UserName, Password and Token

"""

class Api(object):

    def __init__(self, **kwargs):
        """Create API object
        Usage::
            >>> api = api.Api(ip="10.195.153.140", username='admin', password='Grapevine1')
        """

        self.ip = kwargs["ip"]
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.token = None
        self.options = kwargs
        self.endpoint = 'https://'+self.ip

    def get_token(self):
        """Generate new token by making a POST request
        """
        path = "/api/system/v1/auth/token"
        payload={}

        authentication = (self.username, self.password)

        if self.token is not None:
            return self.token
        else:
            self.token = self.http_call(util.join_url(self.endpoint, path), "POST",verify=False, data=payload, auth=authentication)

        return self.token

    def headers(self):
        """Default HTTP headers
        """
        token = self.get_token()

        logging.info("Token is:"+str(token['Token']))

        return {
            "X-Auth-Token": token['Token'],
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def http_call(self, url, method, **kwargs):
        """Makes a http call.
        """
        print('Request[%s]: %s' % (method, url))
        start = datetime.datetime.now()

        print("Method:"+method);
        print("URL:" + url);

        response = requests.request(method, url, **kwargs)

        total = datetime.datetime.now() - start
        print('Response[%d]: %s, Duration: %s.%ss.' % (
        response.status_code, response.reason, total.seconds, total.microseconds))

        status = response.status_code
        result= response.content.decode('utf-8')
        if 200 <= status <= 299:
            return json.loads(result) if result else {}

        return None

    def get(self, action, headers=None):
        """Make GET request
        Usage::
            >>> api.get("/api/v1/network-device")
        """
        http_headers = util.join_header(self.headers(), headers or {})

        return self.request(util.join_url(self.endpoint, action), 'GET', headers=http_headers or {})

    def post(self, action, params=None, headers=None):
        """Make POST request
        Usage::
            >>> api.post("/api/v1/network-device", { 'deviceName': 'AP3800' })
        """
        http_headers = util.join_header(self.headers(), headers or {})
        return self.request(util.join_url(self.endpoint, action), 'POST', body=params or {}, headers=http_headers or {})

    def put(self, action, params=None, headers=None):
        """Make PUT request
        Usage::
            >>> api.put("/api/v1/network-device", { 'name': 'AP-RENAMED'})
        """
        return self.request(util.join_url(self.endpoint, action), 'PUT', body=params or {}, headers=headers or {})


    def delete(self, action, headers=None):
        """Make DELETE request
        """
        return self.request(util.join_url(self.endpoint, action), 'DELETE', headers=headers or {})

    def request(self, url, method, body=None, headers=None):
        """Make HTTP call
        Usage::
            >>> api.request("https://dna.c.cisco.com/api/v1/network-device", "GET", {})
        """
        return self.http_call(url, method, data=json.dumps(body), verify=False,headers=headers)


    __api__ = None

    def set_config(options=None, **config):
        """Create new default api object with given configuration
        """
        global __api__
        __api__ = Api(options or {}, **config)
        return __api__

    configure = set_config
