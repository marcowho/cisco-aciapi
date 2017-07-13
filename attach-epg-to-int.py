#!/usr/bin/env python
"""
Program which attach EPG to interfaces.
Written by: Marco Huang
"""
import acitoolkit.acitoolkit as ACI
import credentials
import csv
from getpass import getpass 

def working_epg_with_int(opt):
	# Login to the APIC
	URL = "https://x.x.x.x"
	#URL = raw_input('APIC Address: ')
	LOGIN = raw_input('Username: ')
	PASSWORD = getpass('Password: ')
	session = ACI.Session(URL, LOGIN, PASSWORD)

	resp = session.login()
	if not resp.ok:
		print('%% Could not login to APIC')

	# Define static vlaues for VLAN encapsulation 
	VLAN = {'name': '',
        	'encap_type': 'vlan'}

	# Define Tenant, AppProfile, and EPG 
	tenant = ACI.Tenant('Corporate')

	with open('VLAN-Trunk-to-ESX.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# print all values as for loop works through CSV file
			print(20 * "=")
			print('Server: ' + str(row['Hostname']))
			print('Port: ' + str(row['Node']) + '/' + str(row['Module']) + '/' + str(row['Port']))
			print('')
			print('APP: ' + str(row['App']))
			print('EPG: ' + str(row['EPG']))
			print('VLAN: ' + str(row['VLAN']))
			print('\r')
			csv_vlan = row['VLAN']
			csv_node = row['Node']
			csv_module = row['Module']
			csv_port = row['Port']

			csv_app = row['App']
			csv_epg = row['EPG']
			app = ACI.AppProfile(csv_app, tenant)
			epg = ACI.EPG(csv_epg, app)

			INTERFACE = {'type': 'eth', 'pod': '1', 'node': csv_node, 'module': csv_module, 'port': csv_port}

			# Create the physical interface object
			intf = ACI.Interface(INTERFACE['type'],
                     		INTERFACE['pod'],
                     		INTERFACE['node'],
                     		INTERFACE['module'],
                     		INTERFACE['port'])

			# Create a VLAN interface and attach to the physical interface
			vlan_intf = ACI.L2Interface(VLAN['name'], VLAN['encap_type'], csv_vlan, "regular")
			vlan_intf.attach(intf)

			domain = ACI.EPGDomain.get_by_name(session, 'Servers')
#			print(domain.name)
			epg.add_infradomain(domain)

			# Attach/Detach the EPG to the VLAN interface
			if opt == 1:
				print('Attaching the EPG from the Interface.')
				epg.attach(vlan_intf)
				# Push it all to the APIC
				print(tenant.get_json())
				resp = session.push_to_apic(tenant.get_url(),tenant.get_json())
				print resp
				print '\r'
				if not resp.ok:
					print('%% Error: Could not push configuration to APIC')
			elif opt == 2:
				print('Detaching the EPG from the Interface.')
				epg.detach(vlan_intf)
				# Push it all to the APIC
				print(tenant.get_json())
				resp = session.push_to_apic(tenant.get_url(),tenant.get_json())
				print resp
				print '\r'
				if not resp.ok:
					print('%% Error: Could not push configuration to APIC')
			elif opt == 3:
				print('Attach dry run.')
				epg.attach(vlan_intf)
				print(tenant.get_json())
			elif opt == 4:
				print('Detach dry run.')
				epg.detach(vlan_intf)
				print(tenant.get_json())


def main():
	print(30 * '-')
	print("   M A I N - M E N U")
	print(30 * '-')
	print("1. Attach EPG to Trunk Interface")
	print("2. Detach EPG to Trunk Interface")
	print("3. Attach Dry run")
	print("4. Detach Dry run")
	print("5. Exit")
	print(30 * '-')
	 
	# Wait for valid input in while...not
	is_valid=0
	 
	while not is_valid :
	        try :
	                choice = int ( raw_input('Enter your choice [1-5] : ') )
	                is_valid = 1 # set it to 1 to validate input and to terminate the while..not loop
	        except ValueError, e :
	                print ("'%s' Use the option number listed." % e.args[0].split(": ")[1])
	 
	# Take action as per selected menu-option
	if choice == 1:
			opt = 1
			print("Attaching...")
			working_epg_with_int(opt)
	elif choice == 2:
			opt = 2
			print("Detaching...")
			working_epg_with_int(opt)
	elif choice == 3:
			opt = 3
			print("Attach dry run...")
			working_epg_with_int(opt)
	elif choice == 4:
			opt = 4
			print("Detach dry run...")
			working_epg_with_int(opt)
	elif choice == 5:
			opt = 5
			print("Bye...")
	else:
			print("Invalid input, try again...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
