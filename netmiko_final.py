from netmiko import ConnectHandler
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

username = os.environ["ROUTER_USER"]
password = os.environ["ROUTER_PASS"]

def gigabit_status(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "host": router_ip,
        "username": username,
        "password": password,
    }

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
            ans = f"Status for {router_ip}: {detail_part} {summary_part}"
            
            return ans
            
    except Exception as e:
        print(f"Netmiko Error: {e}")
        return f"Error: Cannot connect to {router_ip} or run command."

def get_motd(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "host": router_ip,
        "username": username,
        "password": password,
        # (ลบ secret ออก)
    }
    
    try:
        with ConnectHandler(**device_params) as ssh:
            # (ลบ ssh.enable() ออก)
            
            result = ssh.send_command("show banner motd")
            print(f"show banner motd result = \n{result}")

            # (ลบ Error check ของ enable mode ออก)

            if "% No MOTD banner is configured" in result:
                return "Error: No MOTD Configured"
            elif "% Invalid input" in result:
                 # (สำคัญ) ดัก Error กรณีคำสั่งนี้ต้องใช้ Enable Mode
                 return "Error: Command failed (Enable Mode required?)."
            elif result:
                return result.strip()
            else:
                return "Error: No MOTD Configured"
                
    except Exception as e:
        print(f"Netmiko Error for get_motd {router_ip}: {e}")
        return f"Error: Cannot connect to {router_ip} or run command."