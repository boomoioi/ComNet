import socket
import os 

local_ip = "127.0.0.1"
local_port = 12345
command_list = ["ascii", "binary", "bye", "cd", "close", "delete", "disconnect", "get", "ls", "open", "put", "pwd", "quit", "rename", "user"]
command_first = {
    "ascii": "TYPE A",
    "binary": "TYPE I",
    "pwd": 'XPWD'
}

def startSocket(ip, port): 
    try:
        control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_socket.connect((ip, port))
    except Exception as error:
        # print(f"Error connecting to {ip}:{port}: {error}")
        if(f"{error}".split()[1][:-1] == "11001"):
            print(f"Unknown host {ip}")
        return None
    return control_socket

def startFTP():
    control_socket = None

    while True: 
        instruction = input("ftp> ").strip()
        args = instruction.split(" ")
        command = args[0]
        command = command.lower()

        if command not in command_list: 
            print("Invalid command.")
            continue

        if command == "open":
            if (control_socket != None and not control_socket._closed):
                print(f"Already connected to {control_socket.getsockname()[0]}, use disconnect first.")
                continue

            target_ip = "127.0.0.1"
            target_port = 21
            if (len(args) == 1): 
                target_ip = input("To ")
            elif (len(args) == 2):
                target_ip = args[1]
            elif (len(args) == 3):
                target_ip = args[1]
                target_port = int(args[2])
        
            control_socket = startSocket(target_ip, target_port)
            if control_socket == None: 
                continue
            print(f"Connected to {target_ip}.")
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue
            
            command_message = "OPTS UTF8 ON\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            username = input(f"User ({target_ip}:(none)): ").strip()
            command_message = "USER " + username + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                print("Login failed.")
                continue

            password = input("Password: ")
            command_message = "PASS " + password + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print()
            print(message)
            if (message[0] == "5"):
                print("Login failed.")
                continue
            

        elif (control_socket == None or control_socket._closed): 
            if command in ["quit", "bye"]:
                print()
                exit()
            print("Not connected.")
            continue

        elif command == "user": 
            username = ""
            password = ""
            if (len(args) == 1): 
                username = input("Username ")
                command_message = "USER " + username + "\r\n"
                control_socket.sendall(command_message.encode())
                message =  control_socket.recv(2048).decode().strip()
                print(message)
                if (message[0] == "5"):
                    print("Login failed.")
                    continue
                password = input("Password: ")
            elif (len(args) == 2):
                username = args[1]
                command_message = "USER " + username + "\r\n"
                control_socket.sendall(command_message.encode())
                message =  control_socket.recv(2048).decode().strip()
                print(message)
                if (message[0] == "5"):
                    print("Login failed.")
                    continue
                password = input("Password: ")
            elif (len(args) == 3):
                username = args[1]
                command_message = "USER " + username + "\r\n"
                control_socket.sendall(command_message.encode())
                message =  control_socket.recv(2048).decode().strip()
                print(message)
                if (message[0] == "5"):
                    print("Login failed.")
                    continue
                password = args[2]

            command_message = "PASS " + password + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print()
            print(message)
            if (message[0] == "5"):
                print("Login failed.")
                continue

        elif command == "cd": 
            if (len(args) == 1): 
                target = input("Remote directory ")
            elif (len(args) == 2):
                target = args[1]

            command_message = "CWD " + target + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command == "ls": 
            f,s = local_port//256, local_port%256
            port_message = "PORT " + ",".join(local_ip.split("."))+f",{f},{s}\r\n"
            control_socket.sendall(port_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.bind((local_ip, local_port))
            data_socket.listen(8)

            remote_target = ""
            if (len(args) >= 2):
                remote_target = args[1] 

            command_message = "NLST " + remote_target + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            data_connection, _ = data_socket.accept()
            ls_result = b""
            while True:
                data = data_connection.recv(2048)
                if not data:
                    break
                ls_result += data

            ls_result = ls_result.decode()

            if (len(args) == 3):
                with open(args[2], 'w') as file:
                    file.write(ls_result)
            else :
                print(ls_result, end="")

            data_socket.close()        
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command == "delete": 
            target_file = ""
            if (len(args) == 1): 
                target_file = input("Remote file ")
            if (len(args) == 2): 
                target_file = args[1]
            
            command_message = "DELE " + target_file + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command == "rename":
            og_name = ""
            new_name = ""
            if (len(args) == 1):
                og_name = input("From name ")
                new_name = input("To name ")
            elif (len(args) == 2):
                og_name = args[1]
                new_name = input("To name ")
            elif (len(args) == 3):
                og_name = args[1]
                new_name = args[2]
            
            command_message = "RNFR " + og_name + "\r\n"
            control_socket.sendall(command_message.encode())
            status = control_socket.recv(2048).decode().strip()
            print(status)
            if (status[0] == "5"):
                continue
            if (status.split(" ")[0] == "350"):
                command_message = "RNTO " + new_name + "\r\n"
                control_socket.sendall(command_message.encode())
                message =  control_socket.recv(2048).decode().strip()
                print(message)
                if (message[0] == "5"):
                    continue

        elif command == "get":
            remote_target = ""
            local_target = ""
            

            if (len(args) == 1):
                remote_target = input("Remote file ")
                local_target = input("Local file ")
            elif (len(args) == 2):
                remote_target = args[1]
                local_target = args[1]
            elif (len(args) == 3):
                remote_target = args[1]
                local_target = args[2]
                
            f,s = local_port//256, local_port%256
            port_message = "PORT " + ",".join(local_ip.split("."))+f",{f},{s}\r\n"
            control_socket.sendall(port_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.bind((local_ip, local_port))
            data_socket.listen(8)

            command_message = "RETR " + remote_target + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            if (not (len(local_target) >= 2 and local_target[1] == ":")):
                local_target = os.getcwd()+"\\"+local_target

            data_connection, _ = data_socket.accept()
            with open(local_target, 'wb') as local_fp:
                while True:
                    file_data = data_connection.recv(2048)
                    if not file_data:
                        break
                    local_fp.write(file_data)

            # ls_result = data_connection.recv(4096).decode().strip()

            data_socket.close()        
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command == "put": 
            remote_target = ""
            local_target = ""
            

            if (len(args) == 1):
                local_target = input("Local file ")
                remote_target = input("Remote file ")
            elif (len(args) == 2):
                local_target = args[1]
                remote_target = args[1].split("\\")[-1]
            elif (len(args) == 3):
                local_target = args[1]
                remote_target = args[2]

            f,s = local_port//256, local_port%256
            port_message = "PORT " + ",".join(local_ip.split("."))+f",{f},{s}\r\n"
            control_socket.sendall(port_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.bind((local_ip, local_port))
            data_socket.listen(8)
            
            
            command_message = "STOR " + remote_target + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

            if (not (len(local_target) >= 2 and local_target[1] == ":")):
                local_target = os.getcwd()+"\\"+local_target

            data_conn, addr = data_socket.accept()  
            with open(local_target, "rb") as f:
                # Read and send file contents in chunks
                data = f.read(1024)
                while data:
                    data_conn.send(data)
                    data = f.read(1024)

            data_conn.close()
            data_socket.close()
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command in command_first.keys():
            command_message = command_first[command] + "\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue

        elif command in ["bye", "quit", "close", "disconnect"]:
            command_message = "QUIT\r\n"
            control_socket.sendall(command_message.encode())
            message =  control_socket.recv(2048).decode().strip()
            print(message)
            if (message[0] == "5"):
                continue
            control_socket.close()
        
        if command in ["quit", "bye"]:
            print()
            exit()




startFTP()
