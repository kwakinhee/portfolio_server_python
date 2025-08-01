from commonlib.gconf import gconf
gconf.processName = "TestBot"

from twisted.internet import reactor
from commonlib.factory.tcp.gClientFactory import GClientFactory
from bot.testBot import BotTCPClient

reactor.connectTCP('127.0.0.1', 23000, GClientFactory(BotTCPClient))
reactor.run()