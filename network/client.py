import socket
import sys


def join_game(host, port=5555):
    # Connects to the chess server as the second player — you play as black
    # host: the IP address of the player who is hosting (running server.py)
    # port: must match the port the server is using (default 5555)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to {host}:{port}...")
    client_socket.connect((host, port))
    print("Connected!\n")

    # Read the welcome message from the server
    welcome = client_socket.recv(1024).decode()
    print(welcome)

    while True:
        # Wait for a message from the server
        data = client_socket.recv(4096).decode()

        if not data:
            print("Connection lost.")
            break

        print(data)

        # If the game is over, stop
        if "GAME OVER" in data:
            break

        # If it contains OPPONENT_MOVE it means white just played — now it's our turn
        if "OPPONENT_MOVE" in data or "WHITE goes first" in data or "BLACK's turn" in data or "It is now black" in data.lower():
            move = input("Your move (e.g. e7 e5): ").strip()
            client_socket.send(move.encode())

    print("Game over. Disconnecting.")
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <host_ip>")
        print("Example: python client.py 192.168.1.10")
        sys.exit(1)

    join_game(host=sys.argv[1])
