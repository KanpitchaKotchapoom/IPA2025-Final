from netmiko import ConnectHandler
from pprint import pprint

device_ip = "<!!!REPLACEME with router IP address!!!>"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "<!!!REPLACEME with device type for netmiko!!!>",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("<!!!REPLACEME with proper command!!!>", use_textfsm=True)
        for status in result:
            if <!!!Write code here!!!>:
                <!!!Write code here!!!>
                if <!!!Write code here!!!> == "up":
                    up += 1
                elif <!!!Write code here!!!> == "down":
                    down += 1
                elif <!!!Write code here!!!> == "administratively down":
                    admin_down += 1
        ans = <!!!Write code here!!!>
        pprint(ans)
        return ans
