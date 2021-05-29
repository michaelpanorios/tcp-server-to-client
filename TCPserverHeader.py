# Import the socket library
from struct import *
import socket
import binascii

# Host IP to listen to. If '' then all IPs in this interface
serverIP = '127.0.0.1'
# Port to listen to
serverPort = 1000
close = False


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    # Bind the socket
    serverSocket.bind((serverIP, serverPort))
    print ("The server is ready to receive at port", str(serverPort))
    # Listen for connections
    serverSocket.listen()
    while not close:
        # Listen and wait for connection
        conn, addr = serverSocket.accept()

        # Print info: Connected address, Server IP & Port, Client IP & Port
        print("Connected by:", addr)
        print("Server Socket port: ", conn.getsockname())
        print("Client Socket port: ", conn.getpeername())

        # Handle the request
        msg = conn.recv(8)
        print(binascii.hexlify(msg))
        msg_type, msg_length1, msg_length2, msg_name = unpack('HBBs3x', msg)
        print('Total message length without pad='+str(msg_length1+msg_length2))
        # We need to find the final padding
        msg_padSize_number1 = (4 - msg_length1 % 4) % 4
        msg_padSize_number2 = (4 - msg_length2 % 4) % 4
        # Print the total with padding
        print('Total message length with pad='+str(msg_length1+msg_padSize_number1+msg_length2+msg_padSize_number2))
        # Receiving the rest bytes. Total message length in packet + Padding - the initial 4 bytes.
        msg = conn.recv(msg_length1+msg_padSize_number1+msg_length2+msg_padSize_number2)

        # Now, if we didn't have any padding the unpacking string should not have any x's.
        if msg_padSize_number1 == 0 and msg_padSize_number2 == 0:
            unpackString = str(msg_length1)+'s'+str(msg_length2)+'s'
        elif msg_padSize_number1 != 0 and msg_padSize_number2 == 0:
            unpackString = str(msg_length1)+'s'+str(msg_padSize_number1)+'x'+str(msg_length2)+'s'
        elif msg_padSize_number1 == 0 and msg_padSize_number2 != 0:
            unpackString = str(msg_length1)+'s'+str(msg_length2)+'s'+str(msg_padSize_number2)+'x'
        else:
            unpackString = str(msg_length1)+'s'+str(msg_padSize_number1)+'x'+ str(msg_length2)+'s'+str(msg_padSize_number2)+'x'

        # Unpack the rest of the message
        msg_number1, msg_number2 = unpack(unpackString, msg)
        # Decode the string into a utf encoding to be printed out.
        msg_name = msg_name.decode('utf-8')
        msg_number1 = msg_number1.decode('utf-8')
        msg_number2 = msg_number2.decode('utf-8')
        print('Name received is '+msg_name)
        print('Number 1 received is ' + msg_number1)
        print('Number 2 received is ' + msg_number2)

        # We're done receiving. Now we need to do our processing of the packet.
        # We need to send back the following:
        # Message type is 1 (Response)
        msg_type = 1
        # Initial response code is 0 - all ok.
        msg_response_code = 0
        if "0" > msg_number1 > "30000":
            msg_response_code = 1
        if "0" > msg_number2 > "30000":
            msg_response_code = 2
        if msg_number2 == "0" and msg_name == "/":
            msg_response_code = 3

        if msg_response_code == 0:
            if msg_name == "+":
                response = int(msg_number1) + int(msg_number2)
            elif msg_name == "-":
                response = int(msg_number1) - int(msg_number2)
            elif msg_name == "*":
                response = int(msg_number1) * int(msg_number2)
            elif msg_name == "/":
                response = int(msg_number1) / int(msg_number2)
            response_length = len(str(response))
            size = bytes(str(response), 'utf-8')
            size_pad = (4 - response_length % 4) % 4
            if size_pad == 0:
                packString = 'HHH2x' + str(response_length) + 's'
            else:
                packString = 'HHH2x' + str(response_length) + 's' + str(size_pad) + 'x'

        # Now it's time to pack our response.
        message = pack(packString, msg_type, msg_response_code, response_length, size)
        # Send the message through the same connection
        err = conn.sendall(message)
        # Print any errors if any exist
        print(err)
        # Signal (with the flag) to close the socket
        close = True
        # And closing
        conn.close()
        serverSocket.close()