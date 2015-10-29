
import json
import xmltodict
import acitoolkit.acitoolkit as ACI
import sys

def GetTenantList():
	session = ACI.Session('http://172.31.216.24', 'admin', 'scotch123', subscription_enabled=False)
	resp = session.login()

	if not resp.ok:
			print "Could not log in to APIC."
			sys.exit(0)

	TenantList = ACI.Tenant.get(session)

	return TenantList

def main():
	TenantNames = []
	ContractList = []
	entry1 =""
	ContractofInterest = "WebCt"
	TenantsNotHaveContract = []

	session = ACI.Session('http://172.31.216.24', 'admin', 'scotch123', subscription_enabled=False)
	resp = session.login()

	if not resp.ok:
			print "Could not log in to APIC."
			sys.exit(0)

	TenantList = GetTenantList()
	#typeTenantList = type(TenantList)
	#print typeTenantList
	for tenant in TenantList:
		TenantNames.append(tenant.name)
		contracts = ACI.Contract.get(session, tenant)
		HasContractofInterest = 0
		for contract in contracts:
			ContractList.append((tenant.name, contract.name))
			#print tenant.name, "has", contract.name

			#if contract.name == "App_to_Web":
			if contract.name == ContractofInterest:
				HasContractofInterest = 1
				#print "Adding a filter entry to ", contract.name, " for", tenant.name
				entry1 = ACI.FilterEntry('entry1', 
								applyToFrag='no',
                         		arpOpc='unspecified',
                         		dFromPort='5060',
                         		dToPort='5060',
                         		etherT='ip',
                         		prot='tcp',
                         		sFromPort='1',
                         		sToPort='65535',
                         		tcpRules='unspecified',
                         		parent=contract)
				resp3 = tenant.push_to_apic(session)
				if resp3.ok:
					print "Filter has been added to Contract ", contract.name, "for ", tenant.name
					#print "Pushed the following JSON to the APIC"
					#print "URL: " + str(tenant.get_url())
					#print "JSON: " + str(tenant.get_json())
				else:
					print "Failure with adding filter to", contract.name, "for", tenant.name
	
		if HasContractofInterest == 0:
			#print "Tenant ", tenant.name, " does not have a contract named ", ContractofInterest
			TenantsNotHaveContract.append(tenant.name)
			
			
		#print "The following tenants do not have the contract "

	print "The following tenants to not have contract name ", ContractofInterest
	for nothave in TenantsNotHaveContract:
		print "\t\t", nothave
			

if __name__ == '__main__':
        main()