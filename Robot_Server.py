import socket
import json
from ev3dev2.motor import MoveTank, MediumMotor, OUTPUT_B, OUTPUT_C, OUTPUT_A, OUTPUT_D

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the SO_REUSEADDR socket option
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set IP and port
server_socket.bind(("0.0.0.0", 1234))

# Create motor objects
tank = MoveTank(OUTPUT_C, OUTPUT_D)
medium_motor_1 = MediumMotor(OUTPUT_B)
medium_motor_2 = MediumMotor(OUTPUT_A)  # Set this to the port the second medium motor is connected to

# Listen for incoming connections
server_socket.listen(1)

print("Server started. Waiting for a connection...")

buffer = '' # Declare the buffer at the start of your script

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from {}.".format(client_address))
        while True:
            global buffer
            try:
                data = client_socket.recv(1).decode()
                buffer += data
                try:
                    end_of_object_index = buffer.index('}') + 1
                    command_str = buffer[:end_of_object_index]
                    buffer = buffer[end_of_object_index:]  # Remove the parsed command from the buffer
                    command = json.loads(command_str)
                    print("Received command: {}".format(command))  # Print the received command
                
                    left_motor_speed = 0
                    right_motor_speed = 0
                    motor_speed = 0
                    claw_speed = 23


                    # check if key exists in command before trying to access it
                    if 'forward' in command and command['forward']:
                        left_motor_speed += 25
                        right_motor_speed += 25
                        claw_speed = 25
                    if 'backward' in command and command['backward']:
                        left_motor_speed -= 10
                        right_motor_speed -= 10
                    if 'turn_left' in command and command['turn_left']:
                        left_motor_speed += 5
                        right_motor_speed -= 5
                    if 'turn_right' in command and command['turn_right']:
                        left_motor_speed -= 5
                        right_motor_speed += 5
                    if 'o' in command and command['o']:
                        motor_speed = 25
                    if 'p' in command and command['p']:
                        motor_speed = -25

                    # if 'up' in command and command['up']:
                    #     tank.on_for_degrees(50, 50, 90)
                    # if 'down' in command and command['down']:
                    #     tank.on_for_degrees(-50, -50, 90)
                    # if 'left' in command and command['left']:
                    #     tank.on_for_degrees(-50, 50, 90)
                    # if 'right' in command and command['right']:
                    #     tank.on_for_degrees(50, -50, 90)
                    # if 'o' in command and command['o']:
                    #     medium_motor_2.on_for_degrees(25, 90)
                    # if 'p' in command and command['p']:
                    #     medium_motor_2.on_for_degrees(-25, 90)

                    tank.on(left_motor_speed, right_motor_speed)
                    medium_motor_2.on(motor_speed)
                    medium_motor_1.on(claw_speed)
                except ValueError:
                    # This means a complete JSON object has not been received yet. Just continue to accumulate data in the buffer.
                    pass

            except socket.error:
                print("Error reading from socket.")
                break
        
        client_socket.close()
        print("Client disconnected.")
except KeyboardInterrupt:
    # Stop the motors when the server is stopped
    tank.off()
    medium_motor_1.off()
    medium_motor_2.off()
    print('Stopping...')
finally:
    server_socket.close()
    print("Server stopped.")
