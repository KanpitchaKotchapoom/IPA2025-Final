import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.181-184
ROUTER_IP = os.environ["ROUTER_IP"]
ROUTER_USER = os.environ["ROUTER_USER"]
ROUTER_PASS = os.environ["ROUTER_PASS"]

NATIVE_URL = f"https://{ROUTER_IP}/restconf/data/Cisco-IOS-XE-native:native"
OPER_URL = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces-state"
IETF_URL = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = (ROUTER_USER, ROUTER_PASS)


def create(student_id):
    name = f"Loopback{student_id}"
    # --- ใช้ IETF_URL ---
    url = f"{IETF_URL}/interface={name}"

    check_resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if check_resp.status_code == 200:
        print(f"Interface {name} already exists.")
        return f"Cannot create: Interface {name}"

    x = student_id[-3]
    y = student_id[-2:]
    ip_addr = f"172.{x}.{y}.1"

    # --- เปลี่ยน Payload เป็น IETF Model ---
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": name,
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip_addr,
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }

    resp = requests.put(
        url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {name} is created successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Error creating interface: {resp.text}"

def delete(student_id):
    name = f"Loopback{student_id}"
    # --- เปลี่ยน URL ---
    url = f"{IETF_URL}/interface={name}"

    resp = requests.delete(
        url,
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {name} is deleted successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface {name}"

def enable(student_id):
    name = f"Loopback{student_id}"
    # --- เปลี่ยน URL ให้ชี้ไปที่ leaf 'enabled' ของ IETF ---
    url = f"{IETF_URL}/interface={name}/enabled"

    # --- เปลี่ยน Payload ให้ตรงกับโมเดล IETF ---
    # โมเดล Cisco-IOS-XE-native ใช้ "Cisco-IOS-XE-native:enabled"
    # โมเดล ietf-interfaces ใช้ "ietf-interfaces:enabled"
    yangConfig = {"ietf-interfaces:enabled": True}

    resp = requests.put(
        url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {name} is enabled successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot enable: Interface {name}"

def disable(student_id):
    name = f"Loopback{student_id}"
    # --- เปลี่ยน URL ให้ชี้ไปที่ leaf 'enabled' ของ IETF ---
    url = f"{IETF_URL}/interface={name}/enabled"

    # --- เปลี่ยน Payload ให้ตรงกับโมเดล IETF ---
    yangConfig = {
        "ietf-interfaces:enabled": False
    }

    resp = requests.put(
        url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {name} is shutdowned successfully"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface {name}"

def status(student_id):
    name = f"Loopback{student_id}"
    api_url_status = f"{OPER_URL}/interface={name}"

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]

        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {name} is enabled"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {name} is disabled"
        else:
            return f"Interface {name} state is inconsistent (Admin: {admin_status}, Oper: {oper_status})"

    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {name}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Error checking status: {resp.text}"