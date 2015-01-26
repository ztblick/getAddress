#!/usr/bin/python

import sys
import os
import re
import urllib2
import optparse
import signal
import xlwt
from bs4 import BeautifulSoup
from posixpath import basename, dirname, join, split

Status = {}
Nlinks = 0
Downloads = 0
row = 0
wb = xlwt.Workbook()
ws = wb.add_sheet('A Test Sheet')

#-------------------------------  helpers  ------------------------------------#

#from Stackoverflow
class TimeoutError(Exception):
	pass

def timeout_handler(signum, frame):
    raise TimeoutError

def die(message):
	print >> sys.stderr, "Error: " + message
	sys.exit(0)

def testInt(arg):
	try:
		arg = int(arg)
		return arg
	except ValueError:
		die("Invalid non-integer value")

#-------------------------------  getLinks  -----------------------------------#

def getLinks(base, dir, depth):
	global Nlinks
	global Downloads
	global URL
	global wb
	global row
	indent = (args.depth - depth)*2

	#from Stackoverflow
	signal.signal(signal.SIGALRM, timeout_handler)
	signal.alarm(args.timeout)

	#empty URL test
	if not base:
		print " "*indent + "Error - Empty URL"
		return

	#parent reference
	#count = 0
	#while base[0]=='.' and base[1]=='.':
	#	dir = dirname(dir)
	#	base = base[3:]
	#	count += 1

	#child reference 
	# if base[0]=='.':
	# 	base = base[2:]

	path = join(dir, base)

	# if count!=0 and count >= args.depth - depth and base != "liberty.jpg":
	# 	print " "*indent + "../"*count + "%s [external]" % path.replace(URL+"/","")
	# 	return

	#external test
	#if re.search(':', base):
	#	print " "*indent + "%s [external]" % base
	#if we've seen it before
	if path in Status:
		if Status[path]==0:
			print " "*indent + path.replace(URL+"/","") + " [done: success]"
		elif Status[path] > 0:
			print " "*indent + path.replace(URL+"/","") + " [done: fail: " + str(Status[path]) + "]"

	else:

		try:			
			req = urllib2.Request(path)
			conn =  urllib2.urlopen(req)
			content = conn.read()

			Status[path]=0
			Nlinks += 1
			Downloads += 1

			soup = BeautifulSoup(content)			
			for link in soup.find_all('a'):

				this = link.get('href')
				if this:

					address = re.search("mailto:[\w.@]+", this)
					if address:
						#this line cuts off the "mailto:" and adds it to the
						#excel spreadsheet 
						ws.write(row, 1, address.group()[7:])
						row+=1

					elif depth > 0:
						getLinks(this, join(dir, dirname(base)), depth-1)

		except urllib2.URLError, e:
			try:
				Status[path] = e.code
			except AttributeError:
				e.code = "no code available"
				Status[path] = e.code
			print " "*indent + path.replace(URL+"/","") + " [fail: " + str(Status[path]) + "]"
			Nlinks += 1

		except TimeoutError:
			 	Status[path] = "timed out"
				print " "*indent + path.replace(URL+"/","") + " [fail: timed out]"
				Nlinks += 1

#-------------------------------  main  ---------------------------------------#

#from http://pymotw.com/2/optparse/
parser = optparse.OptionParser()
parser.add_option('-d', '--depth', 
                  dest="depth", 
                  default=0,
                  )
parser.add_option('-f', '--folder',
                  dest="folder",
                  default=os.getcwd(),
                  )
parser.add_option('-t', '--timeout',
                  dest="timeout",
                  default=2,
                  )
args, remainder = parser.parse_args()

args.depth = testInt(args.depth)
if args.depth > 5 or args.depth < 0:
	die("Invalid depth value")

args.timeout = testInt(args.timeout)
if args.timeout > 30 or args.timeout < 0:
	die("Invalid timeout value")

if not remainder:
	die("No URL specified")

URL = remainder[0]

try:
	req = urllib2.Request(URL)
	conn =  urllib2.urlopen(req)

	print "URL: %s" % URL
	print "current: %s" % os.getcwd()
	print "target: %s\n" % args.folder

	base = basename(URL)
	URL = dirname(URL)

	getLinks(base, URL, args.depth)
	if row == 1:						#because "one email addresses" would
		print "1 email address found."	#annoy me and only me
	else:
		print "\n%d email addresses found." % (row)
	wb.save('testAddress.xls')

except urllib2.URLError, e:
	die("invalid URL")