#!/usr/bin/python2.6
import pexpect
import time
import sys
from optparse import OptionParser, OptionGroup

parser = OptionParser("usage=%prog [options] filename", version="%prog 0.1")
parser.add_option("--channelsactive", action="store_true", dest="channelsactive", help="Print the total number of channels active.")
parser.add_option("--callsactive", action="store_true", dest="callsactive", help="Print the total number of active calls.")
parser.add_option("--skypeactive", action="store_true", dest="skypeactive", help="Print the total number of Active Skype channels. Print -1 if the module is not active.")
parser.add_option("--g729activeenc", action="store_true", dest="g729activeenc", help="Print the total number of Active g729 Encoders. Print -1 if the module is not active.")
parser.add_option("--g729activedec", action="store_true", dest="g729activedec", help="Print the total number of Active g729 Decoders. Print -1 if the module is not active.")
parser.add_option("--skypelicense", action="store_true", dest="skypelicense", help="Print the total number of Active Skype channels. Print -1 if the module is not active.")
parser.add_option("--g729license", action="store_true", dest="g729license", help="Print the total number of Active g729 channels. Print -1 if the module is not active.")

# Channel lists include up or down Skype channels

# Calls is not nearly as easy as it is in the CLI - show channels shows the number of calls, but the AMI doesn't show the number of calls, nor can it be discerned from the CoreShowChannels data. There's a workaround below, where the Channel has to be up to be considered live, and if two calls are bridged to each other, they are considered one call, but it's ugly.


USERNAME = 'zabbix'
PASSWORD = 'password'

(options, args) = parser.parse_args()

def connect_ami():
    #TODO : Support astmanproxy or build own proxy to handle multiple simultaneous requests.
    child=pexpect.spawn('telnet localhost 5038')
    #child.logfile = sys.stdout
    child.expect("Asterisk Call Manager/1.1\r\n",timeout=1)
    child.setecho(False)
    child.sendline("Action: Login")
    child.sendline("ActionID: 1")
    child.sendline("Username: %s" % USERNAME)
    child.sendline("Secret: %s\r" % PASSWORD)
    child.expect("accepted\r",timeout=1)
    child.sendline("Action: Events")
    child.sendline("EventMask: Off\r")
    child.expect("Events: Off\r")
    return child

def check_module(child,modulename):
    modules = { 
            "Skype" : 'chan_skype.so',
            "G729" : 'codec_g729a.so',
            }

    module = modules[modulename]

    child.sendline("Action: ModuleCheck")
    child.sendline("Module: %s\r" % module)
    i = child.expect(["Success\r","Error\r"])
    if i == 0:
        child.expect("Version: .+")
        return True
    else :
        child.expect("Message: Module not loaded\r")
        return False
#child = connect_ami()
#child.interact()

if options.skypelicense:
    child = connect_ami()
    if check_module(child,"Skype"):
        child.sendline("Action: SkypeLicenseStatus\r")
        child.expect('CallsLicensed: \d+\r',timeout=1)
        result = child.after
    else:
        result = "-1"
if options.skypeactive:
    child = connect_ami()
    if check_module(child,"Skype"):
        child.sendline("Action: CoreShowChannels\r")
        child.expect('ListItems: \d+\r',timeout=1)
        result = child.before.count("\nChannel: Skype")
    else:
        result = "-1"        
elif options.g729license:
    child = connect_ami()
    if check_module(child,"G729"):
        child.sendline("Action: G729LicenseStatus\r")
        child.expect('ChannelsLicensed: \d+\r',timeout=1)
        result = child.after.split(' ')[1]
    else:
        result = "-1"
elif options.g729activeenc:
    child = connect_ami()
    if check_module(child,"G729"):
        child.sendline("Action: G729LicenseStatus\r")
        child.expect('EncodersInUse: \d+\r',timeout=1)
        result = child.after.split(' ')[1]
    else:
        result = "-1"
elif options.g729activedec:
    child = connect_ami()
    if check_module(child,"G729"):
        child.sendline("Action: G729LicenseStatus\r")
        child.expect('DecodersInUse: \d+\r',timeout=1)
        result = child.after.split(' ')[1]
    else:
        result = "-1"        
elif options.channelsactive:
    child = connect_ami()
    child.sendline("Action: CoreShowChannels\r")
    child.expect('ListItems: \d+\r',timeout=1)
    result = child.after.split(' ')[1]
elif options.callsactive:
    child = connect_ami()
    child.sendline("Action: CoreShowChannels\r")
    child.expect('Message: Channels will follow\r',timeout=1)
    child.expect('Event: CoreShowChannelsComplete\r',timeout=1)
    to_parse = child.before[3:-3]
    child.expect('ListItems: \d+\r',timeout=1)
    if child.after.split(' ')[1] != "0\r":
        channels = to_parse.split('\n\r\n')
        callslist = []
        for c in channels:
            callslist.append([ e.split(': ') for e in c.split('\n') ])

        #This is crappy and I know it. Fix next time
        calls=[]
        for c in callslist:
            call = {}
            for v in c :
                call[v[0]]=v[1].strip()
            calls.append(call)

        count = 0
        bridges=[]

        for c in calls:
            if c['ChannelStateDesc'] == 'Up' and c['BridgedChannel'] == '':
                count = count + 1
            elif c['ChannelStateDesc'] == 'Down':
                pass
            else :
                id = c['UniqueID']
                bid = c['BridgedUniqueID']
                if bridges.count(id):
                    #ID already in here. Remove it and call it a call.
                    bridges.remove(id)
                    count = count + 1
                else :
                    bridges.append(bid)
        result = count
    else:
        result = 0
else :
    parser.print_help() #Zabbix won't like this at all.

#TODO: Perhaps fetch all data at once, store in a temp file, and then have script grab from that, and refresh data when stale.
#http://code.activestate.com/recipes/546512/
#http://dwiel.net/blog/single-instance-application-with-command-line-interface/
#http://docs.python.org/library/multiprocessing.html#using-a-pool-of-workers
#http://stackoverflow.com/questions/2031121/detect-if-a-process-is-already-running-and-collaborate-with-it
#http://linux.die.net/man/7/sem_overview
child.sendline("Action: Logoff\r")
child.expect(pexpect.EOF,timeout=1)
child.close
print result
