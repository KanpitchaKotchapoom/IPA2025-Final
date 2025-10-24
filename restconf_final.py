import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.181-184
ROUTER_USER = os.environ["ROUTER_USER"]
ROUTER_PASS = os.environ["ROUTER_PASS"]

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = (ROUTER_USER, ROUTER_PASS)


def create(student_id, router_ip):
    IETF_URL = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    name = f"Loopback{student_id}"
    # --- ใช้ IETF_URL ---
    url = f"{IETF_URL}/interface={name}"

    check_resp = requests.get(url, auth=basicauth, headers=headers, verify=False)
    if check_resp.status_code == 200:
        print(f"Interface {name} on {router_ip} already exists.")
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
        return f"Interface {name} is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot create: Interface {name}"

def delete(student_id, router_ip):
    IETF_URL = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    name = f"Loopback{student_id}"
    url = f"{IETF_URL}/interface={name}"

    resp = requests.delete(
        url,
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {name} is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface {name}"

def enable(student_id, router_ip):
    IETF_URL = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    name = f"Loopback{student_id}"
    url = f"{IETF_URL}/interface={name}/enabled"
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
        return f"Interface {name} is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot enable: Interface {name}"

def disable(student_id, router_ip):
    IETF_URL = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
    name = f"Loopback{student_id}"
    url = f"{IETF_URL}/interface={name}/enabled"
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
        return f"Interface {name} is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface {name} (checked by Restconf)"

def status(student_id, router_ip):
    OPER_URL = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces-state"
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
            return f"Interface {name} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {name} is disabled (checked by Restconf)"
        else:
            return f"Interface {name} state is inconsistent (Admin: {admin_status}, Oper: {oper_status})"

    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface {name} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Error checking status on {router_ip}: {resp.text}"