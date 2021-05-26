###
# Copyright (c) 2021, Stuart Prescott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###


import re
import time


from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Squawker')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Squawker(callbacks.Plugin):
    """Periodically squawks at a channel in response to activity"""

    def __init__(self, irc):
        self.__parent = super(Squawker, self)
        self.__parent.__init__(irc)
        self.throttle = RequestThrottle()
        self.throttle.log = self.log

    def doPrivmsg(self, irc, msg):
        if irc.isChannel(msg.args[0]):
            channel = msg.args[0]

            if not self.registryValue('enabled', channel, irc.network):
                self.log.info("Squawker is disabled for network/channel %s",
                              (irc.network, channel))
                return

            text = self.registryValue('text', channel)

            if self.throttle.permit(msg, text) \
                    and not re.search(self.registryValue('ignored_nicks', channel, irc.network),
                                      msg.nick):
                irc.reply(text)
            self.throttle.record(msg,
                    self.registryValue('throttle', channel, irc.network),
                    text)


class RequestThrottle:
    """ A throttle to control the rate of automated responses """
    def __init__(self):
        self.cache = {}
        self.limit_private = False

    def permit(self, msg, *args):
        """ permit the request according to the throttle conditions
        (False disallows the call) """
        channel = msg.args[0]
        if self.limit_private and not channel.startswith("#"):
            # don't throttle privmsg queries
           return False

        reqid = self._id(channel, *args)
        ts = time.time()
        permit = not (reqid in self.cache and self.cache[reqid] > ts)
        if self.log:
            if permit:
                self.log.info("Permitting request id %s", reqid)
            else:
                self.log.info("Not permitting request %s", reqid)
        return permit

    def _id(self, channel, *args):
        return "/".join((channel,) + args)

    def record(self, msg, timeout, *args):
        """track a timestamp for this throttle """
        channel = msg.args[0]
        reqid = self._id(channel, *args)
        ts = time.time()
        self.cache[reqid] = ts + timeout
        # clean out old timestamps; there will never be enough entries in
        # the cache for performance to be slow enough to be an issue
        [self.cache.pop(k) for k in self.cache.keys() if self.cache[k] < ts]


Class = Squawker


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
