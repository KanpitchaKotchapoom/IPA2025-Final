from netmiko import ConnectHandler
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

device_ip = os.environ["ROUTER_IP"]
username = os.environ["ROUTER_USER"]
password = os.environ["ROUTER_PASS"]

device_params = {
    "device_type": "cisco_ios",
    "host": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    try:
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0
            
            detail_strings = []
            
            result = ssh.send_command("show ip interface brief", use_textfsm=True)
            
            if not isinstance(result, list):
                return "Error: TextFSM failed to parse output."

            for status in result:
                if status['interface'].startswith("GigabitEthernet"):
                    
                    interface_name = status['interface']
                    status_text = ""
                    
                    if status.get('status') == "administratively down":
                        status_text = "administratively down"
                        admin_down += 1
                    elif status.get('status') == "up" and status.get('protocol') == "up":
                        status_text = "up"
                        up += 1
                    else: 
                        status_text = "down"
                        down += 1

                    detail_strings.append(f"{interface_name} {status_text}")
            

            detail_part = ", ".join(detail_strings)
            summary_part = f"-> {up} up, {down} down, {admin_down} administratively down"
            ans = f"{detail_part} {summary_part}"
            
            return ans
            
    except Exception as e:
        print(f"Netmiko Error: {e}")
        return f"Error: Cannot connect to router or run command."