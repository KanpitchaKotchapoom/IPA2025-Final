import os
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xmltodict
from dotenv import load_dotenv

load_dotenv()

ROUTER_USER = os.environ["ROUTER_USER"]
ROUTER_PASS = os.environ["ROUTER_PASS"]
NETCONF_PORT = os.environ.get("NETCONF_PORT", 830)

def create(student_id, router_ip):
    name = f"Loopback{student_id}"
    x = student_id[-3]
    y = student_id[-2:]
    ip_addr = f"172.{x}.{y}.1"

    netconf_config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip_addr}</ip>
              <netmask>255.255.255.0</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=NETCONF_PORT,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {name} is created successfully using Netconf"
            else:
                return f"Cannot create: Interface {name}"

    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Cannot create: Interface {name}"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"Error connecting to {router_ip}"


def delete(student_id, router_ip):
    name = f"Loopback{student_id}"

    netconf_config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>{name}</name>
        </interface>
      </interfaces>
    </config>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=NETCONF_PORT,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {name} is deleted successfully using Netconf"
            else:
                return f"Cannot delete: Interface {name}"
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Cannot delete: Interface {name}"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"Error connecting to {router_ip}"


def enable(student_id, router_ip):
    name = f"Loopback{student_id}"

    netconf_config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=NETCONF_PORT,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {name} is enabled successfully using Netconf"
            else:
                return f"Cannot enable: Interface {name}"
                
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Cannot enable: Interface {name}"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"Error connecting to {router_ip}"


def disable(student_id, router_ip):
    name = f"Loopback{student_id}"

    netconf_config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=NETCONF_PORT,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            hostkey_verify=False
        ) as m:
            netconf_reply = m.edit_config(target="running", config=netconf_config)
            xml_data = netconf_reply.xml
            print(xml_data)
            if '<ok/>' in xml_data:
                return f"Interface {name} is shutdowned successfully using Netconf"
            else:
                return f"Cannot shutdown: Interface {name} (checked by Netconf)"
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"Cannot shutdown: Interface {name} (checked by Netconf)"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"Error connecting to {router_ip}"

# (ฟังก์ชัน netconf_edit_config ถูกรวมเข้าใน try...with... แล้ว)

def status(student_id, router_ip):
    name = f"Loopback{student_id}"

    netconf_filter = f"""
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{name}</name>
        </interface>
      </interfaces-state>
    </filter>
    """

    try:
        with manager.connect(
            host=router_ip,
            port=NETCONF_PORT,
            username=ROUTER_USER,
            password=ROUTER_PASS,
            hostkey_verify=False
        ) as m:
            
            netconf_reply = m.get(filter=netconf_filter)
            print(netconf_reply)
            
            netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

            if ('rpc-reply' in netconf_reply_dict and 
                'data' in netconf_reply_dict['rpc-reply'] and 
                netconf_reply_dict['rpc-reply']['data'] and 
                'interfaces-state' in netconf_reply_dict['rpc-reply']['data'] and 
                netconf_reply_dict['rpc-reply']['data']['interfaces-state']):
                
                interface_data = netconf_reply_dict['rpc-reply']['data']['interfaces-state']['interface']
                
                admin_status = interface_data.get('admin-status')
                oper_status = interface_data.get('oper-status')
                
                if admin_status == 'up' and oper_status == 'up':
                    return f"Interface {name} is enabled (checked by Netconf)"
                elif admin_status == 'down' and oper_status == 'down':
                    return f"Interface {name} is disabled (checked by Netconf)"
                else:
                    return f"Interface {name} state inconsistent (Admin: {admin_status}, Oper: {oper_status})"
            
            else:
                return f"No Interface {name} (checked by Netconf)"
                
    except RPCError as e:
        print(f"Error: {e.message}")
        return f"No Interface {name} (checked by Netconf)"
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"Error connecting to {router_ip}"