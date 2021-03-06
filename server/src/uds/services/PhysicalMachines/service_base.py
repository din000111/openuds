# -*- coding: utf-8 -*-

#
# Copyright (c) 2019-2021 Virtual Cable S.L.U.
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
#    * Neither the name of Virtual Cable S.L.U. nor the names of its contributors
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

"""
@author: Adolfo Gómez, dkmaster at dkmon dot com
"""
import subprocess
import logging
import typing

from uds.core import services

logger = logging.getLogger(__name__)

# We have included a "hidden testing" for adding ip+mac as static machines list.
# (This is done using IP;MAC as IP on the IP list)
# This is a test for WOL, and to be used at your risk.
# Example:
# WOLAPP = "/usr/sbin/etherwake {MAC} -i eth0 -b"
# Remember that you MUST setuid /usr/sbin/etherwake (chmod +s ....) and allow only for uds user,
# so it allows uds user to execute "privileged" etherwake program
# Note:
#   {MAC} will be replaced with the MAC if it exists
#   {IP} will be replaced with the IP of the machine
# If empty, no WOL will be tried NEVER, if not empty
WOLAPP = ''


class IPServiceBase(services.Service):

    @staticmethod
    def getIp(ipData: str) -> str:
        return ipData.split('~')[0].split(';')[0]

    @staticmethod
    def getMac(ipData: str) -> typing.Optional[str]:
        try:
            return ipData.split('~')[0].split(';')[1]
        except Exception:
            return None

    def getUnassignedMachine(self) -> typing.Optional[str]:
        raise NotADirectoryError('getUnassignedMachine')

    def unassignMachine(self, ip: str) -> None:
        raise NotADirectoryError('unassignMachine')

    def wakeup(self, ip: str, mac: typing.Optional[str]) -> None:
        if WOLAPP and mac:
            cmd = WOLAPP.replace('{MAC}', mac or '').replace('{IP}', ip or '')
            logger.info('Launching WOL: %s', cmd)
            try:
                result = subprocess.run(cmd, shell=True, check=True)
                # logger.debug('Result: %s', result)
            except Exception as e:
                logger.error('Error on WOL: %s', e)
