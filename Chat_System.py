import socket
import threading
import rsa

# Generate RSA key pair for secure communication
public_key, private_key = rsa.newkeys(2048)
public_partner = None

try:
    # User chooses to host or connect
    choice = input("Do you want to host (1) or to connect (2): ")

    if choice == "1":
        # Host a server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("192.168.29.225", 9999))
        server.listen()

        # Accept connection from a client and exchange public keys
        client, _ = server.accept()
        client.send(public_key.save_pkcs1("PEM"))
        public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))

    elif choice == "2":
        # Connect to a host and exchange public keys
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("192.168.29.225", 9999))
        public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
        client.send(public_key.save_pkcs1("PEM"))

    else:
        exit()

except Exception as e:
    print(f"An error occurred: {e}")
    exit()

def sending_message(c):
    try:
        while True:
            # Get user input for messages; type 'exit' to end the chat
            message = input("")
            if message.lower() == "exit":
                break

            # Encrypt and send the message to the partner
            encrypted_message = rsa.encrypt(message.encode(), public_partner)
            c.send(encrypted_message)
            print("You: " + message)

    except Exception as e:
        print(f"An error occurred while sending a message: {e}")
    finally:
        try:
            if c.fileno() != -1:  # Check if the socket is still valid
                c.shutdown(socket.SHUT_RDWR)
                c.close()
        except Exception as e:
            print(f"An error occurred while closing the client socket: {e}")

def receiving_message(c):
    try:
        while True:
            # Receive and decrypt messages from the partner
            encrypted_message = c.recv(1024)
            if not encrypted_message:
                break

            decrypted_message = rsa.decrypt(encrypted_message, private_key).decode()
            print("Partner: " + decrypted_message)

    except Exception as e:
        print(f"An error occurred while receiving a message: {e}")
    finally:
        try:
            if c.fileno() != -1:  # Check if the socket is still valid
                c.shutdown(socket.SHUT_RDWR)
                c.close()
        except Exception as e:
            print(f"An error occurred while closing the server socket: {e}")

# Start the threads for sending and receiving messages
send_thread = threading.Thread(target=sending_message, args=(client,))
receive_thread = threading.Thread(target=receiving_message, args=(client,))

send_thread.start()
receive_thread.start()

# Wait for both threads to finish before printing the chat session ending message
send_thread.join()
receive_thread.join()

print("Chat session ended.")

