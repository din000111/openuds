# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Virtual Cable S.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of Virtual Cable S.L. nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
@author: Adolfo Gómez, dkmaster at dkmon dot com
'''
# pylint: disable=invalid-name
import json
import typing

import requests

from ..log import logger

# For avoid proxy on localhost connections
NO_PROXY = {
    'http': None,
    'https': None,
}

class UDSActorClientPool:
    _clientUrl: typing.List[str]

    def __init__(self) -> None:
        self._clientUrl = []

    def _post(self, method: str, data: typing.MutableMapping[str, str], timeout=2) -> typing.List[requests.Response]:
        removables: typing.List[str] = []
        result: typing.List[typing.Any] = []
        for clientUrl in self._clientUrl:
            try:
                result.append(requests.post(clientUrl + '/' + method, data=json.dumps(data), verify=False, timeout=timeout, proxies=NO_PROXY))
            except Exception as e:
                # If cannot request to a clientUrl, remove it from list
                logger.info('Could not connect with client %s: %s. Removed from registry.', e, clientUrl)
                removables.append(clientUrl)

        # Remove failed connections
        for clientUrl in removables:
            self.unregister(clientUrl)

        return result

    def register(self, clientUrl: str) -> None:
        # Remove first if exists, to avoid duplicates
        self.unregister(clientUrl)
        # And add it again
        self._clientUrl.append(clientUrl)

    def unregister(self, clientUrl: str) -> None:
        self._clientUrl = list((i for i in self._clientUrl if i != clientUrl))

    def executeScript(self, script: str) -> None:
        self._post('script', {'script': script}, timeout=30)

    def logout(self) -> None:
        self._post('logout', {})

    def message(self, message: str) -> None:
        self._post('message', {'message': message})

    def ping(self) -> bool:
        if not self._clientUrl:
            return True                  # No clients, ping ok
        self._post('ping', {}, timeout=1)
        return bool(self._clientUrl)     # There was clients, but they are now lost!!!

    def screenshot(self) -> typing.Optional[str]:  # Screenshot are returned as base64
        for r in self._post('screenshot', {}, timeout=3):
            try:
                return r.json()['result']
            except Exception:
                pass
        return None
