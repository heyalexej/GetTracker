#!/usr/bin/env python
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# cfacchini google mail wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -fax
# ----------------------------------------------------------------------------
#
# simply run this file without arguments
#

import urllib2
import re
import json
import sys
import socket
from BeautifulSoup import BeautifulSoup

with open ('ghostery-bugs-mod.json') as f:
    js = json.load (f)

with open ('top-1m.csv') as f:
    hosts = f.readlines ()

# Extract host names of first 100000 entries
hosts = [h.split (',') for h in hosts[:100000]]

result = open ('result.csv', 'a')
err = open ('errors.log', 'a')

# Preparing user agent
uaString = r'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1'


for h in hosts:
    # Specify a timeout to prevent the connection hanging forever
    req = urllib2.Request (url='http://' + h[1][:-1], headers={'User-agent': uaString})
    try:
        webpage = urllib2.urlopen (req, timeout=2)
    except urllib2.HTTPError as e:
        err.write (",".join ([h[0], h[1][:-1], str (e.code), e.msg]))
        err.write ("\n")
        err.flush ()
    except socket.timeout:
        err.write (",".join ([h[0], h[1][:-1], "0", "Socket timeout"]))
        err.flush ()
    except urllib2.URLError:
        err.write (",".join ([h[0], h[1][:-1], "0", "URLlib2 timeout"]))
        err.flush ()
    except: # Generic error
        err.write (",".join ([h[0], h[1][:-1], "0", str (sys.exc_info()[0])]))
        err.flush ()
    else:
        try:
            page = webpage.read ()
        except:
            err.write (",".join ([h[0], h[1][:-1], "0", "Socket timeout"]))
            err.flush ()
            continue

        try:
            soup = BeautifulSoup (page)
        except:
            err.write (",".join ([h[0], h[1][:-1], "0", "BeautifulSoup cannot parse the page"]))
            err.flush ()
            continue

        # Analyze all 'script' tags
        scriptList = soup.findAll('script')
        noScript = len (scriptList)
        trackers = []
        
        for entry in js:
            if noScript:
                R = re.compile (entry['pattern'])
                for tag in scriptList:
                    if R.search (tag.text):
                        trackers.append (entry['name'])
                        # Quit before if there are not any 'script' tags left
                        noScript -= 1

        result.write (",".join ([h[0], h[1][:-1]]))
        result.write (",")
        if trackers:
            # Remove duplicates
            result.write ("|".join (list (set (trackers))))
        result.write (",\n")
        result.flush ()


result.close ()
err.close ()
