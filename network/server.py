import socket
import sys
import os

# Add the project root to the path so we can import our chess classes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game import Game


def start_server(host="0.0.0.0", port=5555):
    # Starts the chess server — the host player plays as white
    # host: the network address to listen on (0.0.0.0 means accept connections from anyone)
    # port: the port number both players must agree on (default 5555)

    game = Game()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow reusing the port immediately after the server stops
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((host, port))
    server_socket.listen(1)  # Wait for exactly 1 connection (the other player)

    print("=== Chess Server ===")
    print(f"Waiting for the other player to connect on port {port}...")

    client_socket, client_address = server_socket.accept()
    print(f"Player 2 connected from {client_address}")
    print("You are WHITE. The other player is BLACK.\n")

    # Send a welcome message to the client
    client_socket.send("You are BLACK. WHITE goes first.\n".encode())

    # Show the starting board to the server player
    print(game.get_board_display())

    while not game.game_over:
        if game.current_turn == "white":
            # It is the server player's turn (white)
            move = input("Your move (e.g. e2 e4): ").strip()
            result = game.play_move(move)
            print(result)

            # Send the move and the result to the other player
            message = f"OPPONENT_MOVE:{move}\nRESULT:{result}\nBOARD:\n{game.get_board_display()}"
            client_socket.send(message.encode())

        else:
            # Wait for the other player's move
            print("Waiting for black's move...")
            data = client_socket.recv(1024).decode().strip()

            if not data:
                print("Connection lost.")
                break

            result = game.play_move(data)
            print(f"Black played: {data}")
            print(result)
            print(game.get_board_display())

            # Send the result back to the client
            response = f"RESULT:{result}\nBOARD:\n{game.get_board_display()}"
            client_socket.send(response.encode())

    print("Game over. Closing connection.")
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    start_server()
