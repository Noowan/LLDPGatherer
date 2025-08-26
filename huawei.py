import os
import re
import time
import paramiko
from paramiko.channel import Channel
from dotenv import load_dotenv

load_dotenv('credentials.env')
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

def connect_ssh(IP: str, DeviceName: str="NONAME") -> Channel:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"trying {DeviceName}, {IP}")
    try:
        client.connect(hostname=IP,
                      username=SSH_USER,
                      password=SSH_PASSWORD,
                      look_for_keys=False,
                      allow_agent=False,
                      timeout=10)
    except Exception as e:
        print(f"{DeviceName},{IP}. Not connected. Reason {e}")
        client.close()
        time.sleep(0.5)
        return
    try:
        shell = client.invoke_shell()
        print(f"{DeviceName}, {IP}. Connected.")
        return shell
    except Exception as e:
        print(f"{DeviceName},{IP}. Can't invoke shell. Reason {e}")
        client.close()


def get_lldp_info(_device):
    shell = connect_ssh(_device[0],_device[1])
    if shell == None:
        return
    try:
        print("Getting lldp info....")
        shell.send("screen-length 0 temporary\n")
        time.sleep(1)
        shell.send(f"display lldp neighbor interface {_device[2]}\n")
        time.sleep(5)
        output = shell.recv(102400).decode()
    except Exception as e:
        print(e)
    sysname = re.search("System name         :.+", output)[0].split(sep=':')
    nbrportid = re.search("Port ID        :.+", output)[0].split(sep=':')
    sysname = sysname[1].replace("\r", "")
    nbrportid = nbrportid[1].replace("\r", "")
    nbrportid = nbrportid[1].replace("GigabitEthernet", "Gi")
    return sysname, nbrportid