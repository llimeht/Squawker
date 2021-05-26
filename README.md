# Squawker: Periodically squawks at a channel

This plugin will make a repeated announcement to a channel, but only in
response to a message being sent to the channel.

Example, repeat this message at most once every 10 minutes:

        @load squawker
        @config supybot.plugins.squawker.throttle 600
        @config channel supybot.plugins.squawker.text Hello! You please
        @config channel supybot.plugins.squawker.enabled True


Squawker is disabled by default and can be enabled on a per-channel basis; it
supports the network-specific options so it can be enabled in #channel on one
irc network while being disabled in the #channel on another network.
