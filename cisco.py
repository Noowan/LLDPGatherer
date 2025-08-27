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
        shell.send("terminal length 0\n")
        time.sleep(1)
        islldpSuccessFlag = True
        shell.send(f"show lldp neighbors {_device[2]} detail\n")
        time.sleep(5)
        output = shell.recv(102400).decode()
        if output.find("LLDP is not enabled") != -1:
            islldpSuccessFlag = False
            shell.send(f"show cdp neighbors {_device[2]} detail\n")
            time.sleep(5)
            output = ""
            output = shell.recv(102400).decode()
        shell.close()
    except Exception as e:
        print(e)

    try:
        if islldpSuccessFlag:
            sysname = re.search("System Name:.+", output)[0].split(sep=':')
            nbrportid = re.search("Port id: .+", output)[0].split(sep=':')
            sysname = sysname[1].replace("\r", "")
            nbrportid = nbrportid[1].replace("\r", "")
            return sysname, nbrportid
        sysname = re.search("Device ID:.+", output)[0].split(sep=':')
        nbrportid = re.search("Port ID \(outgoing port\): .+", output)[0].split(sep=':')
        sysname = sysname[1].replace("\r", "")
        nbrportid = nbrportid[1].replace("\r", "")
        return sysname, nbrportid
    except:
        return "NULL", "NULL"