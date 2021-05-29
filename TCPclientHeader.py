from struct import *
import socket 
import binascii

# Host IP to send to.
serverIP = '127.0.0.1'
# Port to send to
serverPort = 1000

# Create the client socket
# socket.AF_INET == IPv4
# socket.SOCK_STREAM == TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect. The server socket should be listening.
clientSocket.connect((serverIP, serverPort))


#  0------------16-------------------31
#  |   Type      |  Length1 , Length2 |    # type:2 byte, length1:1byte, length2:1byte
#  0-------------+-------------------31
#  |          operator                |    # operator: 1 byte, padding 3 bytes
#  0---------------------------------31
#  |         number1(+pad)            |    # number1: 4 byte
#  0---------------------------------31
#  |         number2(+pad)            |    # number2: 4 byte
#  0---------------------------------31


# Create the data for the header
msg_type = 0
print("Please enter the first number: ")
msg_number1 = input()
print("Please enter the second number: ")
msg_number2 = input()
print("Please enter an operator: ")
operator = input()
while operator != "+" and operator != "-" and operator != "*" and operator != "/":
    print("Please re-enter an operator: ")
    operator = input()
msg_name = bytes(operator, 'utf-8')
# Total message length
msg_length1 = len(msg_number1)
msg_length2 = len(msg_number2)
# Encode the name as bytes with encoding utf-8
nb1 = bytes(msg_number1, 'utf-8')
nb2 = bytes(msg_number2, 'utf-8')

# Calculate the pad size
# The padding size should be calculated as such:
# As messages are 4 bytes aligned, we need to find how many bytes are in the name
# Find the remainder of the bytes of the name divided by 4 (modulo)
# This number is how much exceed from 4. So we need to subtract that from 4 in order to find how many bytes are needed.
# However if the modulo is 0, then 4-modulo (padding) would be 4, which is not correct. It's already aligned!
# So, we do another modulo to be sure that the value does not go over 4

msg_padSize_number1 = (4 - len(msg_number1) % 4) % 4
msg_padSize_number2 = (4 - len(msg_number2) % 4) % 4

# Create a packing string (since we know the )
if msg_padSize_number1 == 0 and msg_padSize_number2 == 0:
    packString = 'HBBs3x'+str(len(msg_number1))+'s'+str(len(msg_number2))+'s'
elif msg_padSize_number1 != 0 and msg_padSize_number2 == 0:
    packString = 'HBBs3x'+str(len(msg_number1))+'s'+str(msg_padSize_number1)+'x'+str(len(msg_number2))+'s'
elif msg_padSize_number1 == 0 and msg_padSize_number2 != 0:
    packString = 'HBBs3x' + str(len(msg_number1))+'s'+str(len(msg_number2))+'s'+str(msg_padSize_number2)+'x'
else:
    packString = 'HBBs3x' +str(len(msg_number1))+'s'+str(msg_padSize_number1)+'x'+ str(len(msg_number2))+'s'+str(msg_padSize_number2)+'x'
# Pack the message
message = pack(packString, msg_type, msg_length1, msg_length2, msg_name,  nb1,  nb2)

# Send the message through the socket
clientSocket.sendall(message)

# Wait for a response (we know we'll receive 8 bytes)
modifiedMessage = clientSocket.recv(8)

# Unpack the message
msg_type, msg_response_code, response_length = unpack('HHH2x', modifiedMessage)

# Print it as hex just for the fun of it
print(binascii.hexlify(modifiedMessage))

# Process the response
if msg_response_code == 0:
        size_pad = (4 - response_length % 4) % 4
        modifiedMessage = clientSocket.recv(response_length+size_pad)
        if (size_pad == 0):
            unpackString = str(response_length) + 's'
        else:
            unpackString = str(response_length) + 's' + str(size_pad) + 'x'
        size = unpack(unpackString, modifiedMessage)
        size = size[0].decode('utf-8')
        print(size)
elif msg_response_code == 1:
        print("Number 1 out of bounds")
elif msg_response_code == 2:
        print("Number 2 out of bounds")
elif msg_response_code == 3:
        print("Both numbers are out of bounds")


# Close the socket
clientSocket.close()