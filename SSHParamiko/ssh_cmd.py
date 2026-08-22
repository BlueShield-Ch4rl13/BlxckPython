import paramiko

def execute_ssh_command(hostname, username, password, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- OUTPUT ---')
        for line in output:
            print(line.strip())

if __name__ == "__main__":
    import getpass
    # user = getpass.getuser()
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    ip = input("Enter IP address: ")
    port = input("Enter port (default 22): ")
    cmd = input("Enter command to execute (default id): ")

    execute_ssh_command(ip, port, username, password, cmd)
    