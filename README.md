#Usage

# Introduction #

This script fetches values from Asterisk using the Asterisk Manager Interface (AMI) and presents them to Zabbix.

Python is required.

# Requires #
Python 2.4+
Asterisk 1.6+
Zabbix 1.4+

# Making it work #

## Asterisk ##
Modify /etc/asterisk/manager.conf and include this block.
```
[zabbix]
secret=password
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.0
read = system,call,log,verbose,command,agent,user
write = system,call,log,verbose,command,agent,user
```

Please change the password, and then restart asterisk.

## Script Install ##

Ensure that you have the necessary packages, download the script and place it wherever you want to. (RIZ, update the link!) I chose to put it in /etc/zabbix. Set it's permissions to run for all users.
```
sudo easy_install posix_ipc
sudo easy_install pexpect
# Download the py file into /etc/zabbix/zasterisk.py

chmod a+x /etc/zabbix/zasterisk.py
```

Edit the first line of zasterisk.py from `#!/usr/bin/python2.6` to the location of the Python interpreter on your machine. Set the password to whatever you set it in the Asterisk step.

Before you go any further, test the script to see if it works for you.

```
/etc/zabbix/zasterisk.py --channelsactive
```

Continue forward only if you get a proper result, otherwise stop here and debug.
(Delete the zasterisk file in /dev/shm after testing, else you'll have perms problems.)

## Zabbix Agent ##

Add the following lines to your Zabbix Agent config.

```
UserParameter=asterisk.activeskypechannels,/etc/zabbix/zasterisk.py --skypeactive
UserParameter=asterisk.activecalls,/etc/zabbix/zasterisk.py --callsactive
UserParameter=asterisk.activechannels,/etc/zabbix/zasterisk.py --channelsactive
UserParameter=asterisk.totalskypechannels,/etc/zabbix/zasterisk.py --skypelicense
UserParameter=asterisk.activeg729encoders,/etc/zabbix/zasterisk.py --g729activeenc
UserParamater=asterisk.activeg729decoders,/etc/zabbix/zasterisk.py --g729activedec
UserParameter=asterisk.totalg729channels,/etc/zabbix/zasterisk.py --g729license
```

Restart your Zabbix agent.


## Zabbix Server ##

TODO, setup graphs, items, triggers.


# Details #

Add your content here.  Format your content with:
  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages