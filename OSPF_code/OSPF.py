from netmiko import ConnectHandler
from ipaddress import IPv4Address
import time

start_time = time.time()

def configure_ospf(i, connection):
    output = connection.send_command("show ip interface brief")
    print("Configuring OSPF in Device: " + hostname)
    interface_and_ip = []
    for line in output.splitlines()[1:]:
        columns = line.split()
        if len(columns) >= 4 and columns[1] != 'unassigned':
            interface_name = columns[0]
            ip_address = columns[1]
            interface_and_ip.append((interface_name, ip_address))
    router_id = f"{i}.{i}.{i}.{i}"

    ospf_commands = [
        f"interface loopback0",
        f"ip address {router_id} 255.255.255.255",
        f"exit",
        f"router ospf 10",
        f"router-id {router_id}",
    ] + [f"network {ip_address} 0.0.0.0 area 0" for _, ip_address in interface_and_ip] + [
        f"passive-interface loopback0",
    ]
    output = connection.send_config_set(ospf_commands)
    print(output)
    print('OSPF is now configured!')

def save_ospf_output_to_file(connection, filename, i):
    output = connection.send_command('show ip ospf')
    with open(filename, 'a') as file:
        file.write(f"\n\n{'='*20} OSPF Output R{i}{' '}{'='*20}\n")
        file.write(output)

my_devices = ['192.168.122.183', '192.168.122.160',
              '192.168.122.202', '192.168.122.8']
device_list = []

for device_ip in my_devices:
    device = {
        "device_type": "cisco_ios",
        "host": device_ip,
        "username": "admin",
        "password": "admin"
    }
    device_list.append(device)

for i, each_device in enumerate(device_list, start=1):
    with ConnectHandler(**each_device) as connection:
        connection.enable()
        output = connection.send_command('show run | inc hostname')
        hostname = output[9:].strip()
        hostname.split(" ")
        print(f'\nConnecting to {each_device["host"]}')
        
        output = connection.send_command('show ip ospf')
        if not 'Routing Process' in output:
            print('OSPF is not enabled on device: ' + hostname)
            answer = input(f'Would you like to enable OSPF configurations on: {each_device["host"]} <y/n> ')
            if answer == 'y':
                configure_ospf(i, connection)
                print(f'Saving OSPF configuration of '+ hostname)   
                save_ospf_output_to_file(connection, 'ospf_output.txt', i)  
            else:
                print("No OSPF configurations have been made on device " + hostname)
        else:
            print(f'OSPF had already been configured on '+ hostname + '!')   
        print(f'Closing Connection on {each_device["host"]}')
        connection.disconnect()

end_time = time.time()
total_time = int(end_time - start_time)
print("\nElapsed Time: " + str(total_time) + " Sec\n")
