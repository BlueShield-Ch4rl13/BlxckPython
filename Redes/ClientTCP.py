import socket

target_host = "www.google.com"  # Target host to connect to Victima 80 and 443
target_port = 80 and 443  # Target port to connect to Victima 80 and 443

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# Send some data
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# Receive some data
response = client.recv(4096)

print(response.decode())
client.close()
