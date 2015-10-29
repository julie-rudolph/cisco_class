#!/usr/bin/env python
from device import Device
import json
import xmltodict
import urllib2
import time
#debug dump
def dumpOutput(output,flag=True):
	if flag:
		print json.dumps(xmltodict.parse(output[1]),indent = 4)

class root_Device:
	def __init__(self,hostname,proccesor_ID,version):
		self.neighbors = []
		self.proccesor_ID = proccesor_ID
		self.hostname = hostname
		self.version = version
		self.ipIntBrief = []
		self.vrfList = []
		self.intStatus = []
		self.portChannels = []
		self.numofvrfs = 0
		self.tcampcents = {}

	def addNeighbor(self,neighbor):
		self.neighbors.append(neighbor)
	def addIp(self,ip):
		self.ipIntBrief.append(ip)
	def addIntStatus(self,interface):
		self.intStatus.append(interface)
	def addVrf(self,vrf):
		self.vrfList.append(vrf)
	def addPortChannel(self,channel):
		self.portChannels.append(channel)		
	def addNumofVrfs(self,numofvrfs):
		self.numofvrfs = numofvrfs
	def addTcamPcts(self,tcampcents):
		self.tcampcents = tcampcents

class Neighbors:
	def __init__(self,NeighborRootDevice,NeighborDict):
		self.rootDevice = NeighborRootDevice
		self.NeighborDict = NeighborDict

class Vrf:                    
	def __init__(self,name):
		self.prefixList = []
		self.name = name     
	def addPrefix(self,prefix):
		self.prefixList.append(prefix)

def get_cdp_info(sw1):
	sh_neigh = sw1.show('show cdp neighbor detail')
	sh_neigh_dict = xmltodict.parse(sh_neigh[1])
	neighbors = sh_neigh_dict['ins_api']['outputs']['output']['body']["TABLE_cdp_neighbor_detail_info"]['ROW_cdp_neighbor_detail_info']
	return neighbors

def get_portchannel_sum(sw1):
	sh_chan = sw1.show('show port-channel summary')
	sh_chan_dict = xmltodict.parse(sh_chan[1])

	if sh_chan_dict['ins_api']['outputs']['output']['body'] != None:
		portChannels = sh_chan_dict['ins_api']['outputs']['output']['body']["TABLE_channel"]['ROW_channel']
		return portChannels

def get_hostname_serial_version(sw1):
	sh_ver= sw1.show('show version')
	sh_ver_dict = xmltodict.parse(sh_ver[1])
	proccesor_ID = sh_ver_dict['ins_api']['outputs']['output']['body']["proc_board_id"]
	hostname = sh_ver_dict['ins_api']['outputs']['output']['body']["host_name"]
	version = sh_ver_dict['ins_api']['outputs']['output']['body']["kickstart_ver_str"]
	return hostname,proccesor_ID,version

def get_ip_int_b(sw1):
	sh_ip_b =  sw1.show('show ip int brief')
	sh_ip_b_dict = xmltodict.parse(sh_ip_b[1])
	int_brief = sh_ip_b_dict['ins_api']['outputs']['output']['body']["TABLE_intf"]
	return int_brief

def get_vrf(sw1):
	sh_ip_vrf = sw1.show("sh ip route vrf all")
	sh_ip_vrf_dict = xmltodict.parse(sh_ip_vrf[1])
	sh_vrf = sh_ip_vrf_dict['ins_api']['outputs']['output']['body']["TABLE_vrf"]["ROW_vrf"]
	return sh_vrf

def get_all_vrfs(sw1):
	show_vrf = sw1.show("show vrf")
	show_vrf_dict = xmltodict.parse(show_vrf[1])
	typeshowvrf = type(show_vrf_dict)
	#print typeshowvrf
	#for key in show_vrf:
	#	print key
	sh_vrf_all = show_vrf_dict['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']
	typeshow_vrf_all = type(sh_vrf_all)
	#print typeshow_vrf_all
	localnumofvrfs = len(sh_vrf_all)
	#print numofvrf
	return localnumofvrfs

def check_tcam(sw1):
	## DO NOT USE - HAS FAULTY LOGIC
	t_sw1 = type(sw1)
	tcampctage_dict = {}
	#print t_sw1
	tcam_results = sw1.show('show hardware access-list resource utilization')
	tcam_results_dict = xmltodict.parse(tcam_results[1])
	tcam_result_parsed = tcam_results_dict['ins_api']['outputs']['output']['body']['TABLE_module']['ROW_module']
	#tcam_result_parsed = tcam_results_dict['ins_api']['outputs']['output']['body']['TABLE_module']
	#tcam_type = type(tcam_result_parsed)
	#tcam_length = len(tcam_result_parsed)
	#print tcam_type, "is", tcam_length

	#for k, v in tcam_result_parsed.iteritems():
	#	print "### KEY IS ", k
	#	print "### VALUE IS ", v
	modulenum = tcam_result_parsed['module_number']	
	#print "module num is ", modulenum
	resourceinfo = tcam_result_parsed['TABLE_resource_util_info']['ROW_resource_util_info']
	typeresourceinfo = type(resourceinfo)
	# print typeresourceinfo
	for tr in resourceinfo:
		#print "tr is", tr
		resource_header = tr['resource_hdr']
		try:
			ents_pctage = tr['ents_pctage']
			t_ents_pctage = type(ents_pctage)
			#print ents_pctage, "is of type", t_ents_pctage
			float_ents_pctage = float(ents_pctage)
			float_ents_pctage_type = type(float_ents_pctage)
			#print float_ents_pctage_type
		except:
			#print "An exception happened in check_tcam"
			pass
		#print "Module", modulenum, "resource header of", resource_header, "has", float_ents_pctage, "percentage util."
		if float_ents_pctage > 0:
			#print modulenum, resource_header, "is greater than 0:", float_ents_pctage
			TcamPcts = [modulenum, resource_header, float_ents_pctage]
			tcampctage_dict.update({'modnum': modulenum, 'res_header': resource_header, 'pctage_util': float_ents_pctage})
			#tcampctage_dict.update([{'modnum': modulenum, 'res_header': resource_header, 'pctage_util': float_ents_pctage}])
			#tcampctage_dict.update([{'modnum': modulenum, ['res_header': resource_header, 'pctage_util': float_ents_pctage]}])
			#campctage_dict['modnum'] = modulenum
			#tcampctage_dict['res_header'] = resource_header
			#tcampctage_dict['pctage_util'] = float_ents_pctage

	#typeoftcamppctage_dict = type(tcampctage_dict)
	#print typeoftcamppctage_dict
	#print tcampctage_dict
	return tcampctage_dict
		 
def get_int_status(sw1):
	sh_status =  sw1.show('show interface status')
	sh_status_dict = xmltodict.parse(sh_status[1])
	int_status = sh_status_dict['ins_api']['outputs']['output']['body']["TABLE_interface"]["ROW_interface"]
	return int_status


def crawlDevice(ip_address,user,pw):

	sw1 = Device(ip=ip_address, username=user, password=pw)
	sw1.open()

	# Getting everything into dicts
	sh_vrf = get_vrf(sw1)
	int_brief = get_ip_int_b(sw1)
	int_status = get_int_status(sw1)
	hostname,proccesor_ID,version = get_hostname_serial_version(sw1)
	neighbors = get_cdp_info(sw1)
	port_channels = get_portchannel_sum(sw1)
	numofvrfs = get_all_vrfs(sw1)
	#tcam_pct_util = check_tcam(sw1)
	#print numofvrfs
	#print tcam_pct_util
	#Adding all data into objs
	LocalDevice = root_Device(hostname,proccesor_ID,version)
	for singleVrf in sh_vrf:
		vrf = Vrf(singleVrf["vrf-name-out"])
		if "TABLE_prefix" in singleVrf["TABLE_addrf"][ "ROW_addrf"].keys():
			for prefixes in singleVrf["TABLE_addrf"][ "ROW_addrf"]["TABLE_prefix"]["ROW_prefix"]:
				vrf.addPrefix(prefixes["ipprefix"])
			LocalDevice.addVrf(vrf)

	for ipInter in int_brief:
		LocalDevice.addIp(ipInter["ROW_intf"]["prefix"])

	LocalDevice.addPortChannel(port_channels)
	for interface in int_status:
		LocalDevice.addIp(interface)

	for neighbor in neighbors:
		neighEntry = Neighbors(root_Device,neighbor)
		LocalDevice.addNeighbor(neighEntry)

	LocalDevice.addNumofVrfs(numofvrfs)

	#LocalDevice.addTcamPcts(tcam_pct_util)

	return LocalDevice

def info_crawl(seedIp,user,password):
	discoveredObjs =[]
	crawledSerials = []
	uncrawled=[seedIp]
	crawledIps =[]
	for ipN in uncrawled:
		try:
			if ipN  not in crawledIps:
				newD = crawlDevice(ipN, user, password)
				crawledIps.append(ipN)
				#print "Connection established to:", ipN
				if newD.proccesor_ID not in crawledSerials:
					crawledSerials.append(newD.proccesor_ID)
					discoveredObjs.append(newD)
					for neigh in newD.neighbors:
						neighborIp = (str(neigh.NeighborDict["v4mgmtaddr"]))
						if neighborIp not in uncrawled:
							uncrawled.append(neighborIp)
						#print "\t",neigh.NeighborDict["v4mgmtaddr"], "DISCOVERED"	
		except urllib2.HTTPError:
			print "[!]Cannont establish to:",ipN
		except Exception as e:
			print "[!]ERROR: ",e
	print "--------CDP Crawl Complete--------\n"
	return discoveredObjs

def main():
	seed = "172.31.217.135"
	username = "admin"
	password = "cisco123"
	devices_Crawled = info_crawl(seed,username,password)	
	for d in devices_Crawled:
		#print "Device", d.hostname, "has", d.numofvrfs, "vrfs."
		print "### UTILIZATION REPORT FOR DEVICE:", d.hostname, "###"
		print "		Number of VRFs Configured:", d.numofvrfs

if __name__ == '__main__':
	main()


