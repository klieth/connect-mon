#!/usr/bin/python2
from __future__ import with_statement
import gtk
import gobject
import os
import subprocess
import os.path
import socket

TIMEOUT = 5

def default_interface():
	'''returns the interface of the default route'''
	interface = None
	stdout = subprocess.check_output(['ip', 'route', 'list', 'scope', 'global'])
	for line in stdout.split('\n'):
		route = line.split(' ')
		if (len(route) >= 5 and (route[0],route[1],route[3]) == ('default','via','dev')):
			interface = route[4]
			break
	return interface

def carrier_ok(iface):
	'''check if the interface is connected'''
	iface_dir = '/sys/class/net/%s' % iface
	with open(iface_dir + '/carrier') as f:
		line = f.next().strip()
		return line == '1'

def get_resource_path(res):
	dir_of_py_file = os.path.dirname(__file__)
	rel_path = os.path.join(dir_of_py_file, res)
	abs_path = os.path.abspath(rel_path)
	print abs_path
	return abs_path

def interface_type(iface):
	if iface == None:
		return 'disconnected'
	res = 'wired'
	iface_dir = '/sys/class/net/%s' % iface
	with open(iface_dir + '/type') as f:
		line = f.next().strip()
		if line == '1':
			res = 'wired'
			if ('wireless' in os.listdir(iface_dir) or
					'phy80211' in os.listdir(iface_dir)):
				res = 'wireless'
	return res

def wpa_status():
	'''returns the output of wpa_cli status.'''
	#return subprocess.check_output(['sudo', 'wpa_cli', 'status']).strip()
	#return 'Other info here'
	iwconfig = subprocess.check_output("iwconfig wlan0 | grep ESSID | cut -d: -f2",shell=True)
	out = "SSID: " + iwconfig.replace("\"","") + "Local IP: " + socket.gethostbyname(socket.getfqdn())
	return out
	

def wifi_strength():
	#pct = subprocess.check_output(['awk', '\'NR==3 {print $3}\'\'\'', '/proc/net/wireless'])
	pct = 61
	stdout = subprocess.check_output(['cat', '/proc/net/wireless'])
	tokens = [[token for token in line.split()] for line in stdout.split('\n')[2:]]
	pct = int(tokens[0][2].split('.')[0])
	if pct < 17:
		return 0
	elif pct < 34:
		return 1
	elif pct < 50:
		return 2
	elif pct < 67:
		return 3
	elif pct < 84:
		return 4
	return 5

class MainApp:
	def __init__(self):
		self.icon = gtk.StatusIcon()
		self.update_icon()
		gobject.timeout_add_seconds(TIMEOUT, self.update_icon)

	def get_network_info(self):
		interface = default_interface()
		connected = False
		if interface:
			connected = carrier_ok(interface)
		return {'interface':interface,'connected':connected}

	def get_icon_name(self, interface, connected):
		icon_name = 'network-disconnected'
		itype = interface_type(interface)
		if connected and itype == 'wireless':
			icon_name = 'network-wireless-%s' % wifi_strength()
		elif connected:
			icon_name = 'network-%s' % itype
		return icon_name

	def get_tooltip(self, interface, connected):
		if not connected:
			res = 'Disconnected'
		else:
			res = 'Connected on %s' % interface
			if interface_type(interface) == 'wireless':
				res = '\n'.join([res, wpa_status()])
		return res

	def update_icon(self):
		info = self.get_network_info()
		icon_name = self.get_icon_name(info['interface'], info['connected'])
		self.icon.set_from_file(get_resource_path(icon_name + '.png'))
		tooltip = self.get_tooltip(info['interface'], info['connected'])
		self.icon.set_tooltip_text(tooltip)
		return True

if __name__ == '__main__':
	try:
		MainApp()
		gtk.main()
	except KeyboardInterrupt:
		pass
