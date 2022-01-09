import asyncio
from textwrap import dedent


class ConnectionPool:
    def __init__(self):
        self.connection_pool = set()

    def send_welcome_message(self, writer):
        """
        Sends a welcome message to a newly connected client
        """

        message = dedent(
            f"""
        ===
        Welcome {writer.nickname}!

        There are {len(self.connection_pool) - 1} user(s) here beside you

        Help:
            - Type anything to chat
            - /list: lists all connected users
            - /quit: quits connection
        ===
        """
        )

        writer.write(f"{message}\n".encode())

    def broadcast(self, writer, message):
        """
        Broadcasts a general message to the entire pool
        """

        for user in self.connection_pool:
            if user != writer:
                user.write(f"{message}\n".encode())

    def broadcast_user_join(self, writer):
        """
        Calls the broadcast method with a "user joining" message
        """

        self.broadcast(writer, f"{writer.nickname} just joined.")

    def broadcast_user_quit(self, writer):
        """
        Calls the broadcast method with a "user quitting" message
        """

        self.broadcast(writer, f"{writer.nickname} just quit.")

    def broadcast_new_message(self, writer, message):
        """
        Call the broadcast method with a user's chat message
        """

        self.broadcast(writer, f"[{writer.nickname}]:{message}")

    def list_users(self, writer):
        """
        Lists all users in the pool
        """

        message = "===\n"
        message += "Currently connected users:"
        for user in self.connection_pool:
            if user == writer:
                message += f"\n - {user.nickname} (you)"
            else:
                message += f"\n - {user.nickname}"

        message += "\n==="
        writer.write(f"{message}\n".encode())

    def add_new_user_to_pool(self, writer):
        """
        Adds a new user to existing pool
        """
        self.connection_pool.add(writer)

    def remove_user_from_pool(self, writer):
        """
        Removes an existing user from the pool
        """
        self.connection_pool.remove(writer)


async def handle_connection(reader, writer):
    writer.write("Hello user, choose your nickname: ".encode())

    response = await reader.readuntil(b"\n")

    writer.nickname = response.decode().strip()

    connection_pool.add_new_user_to_pool(writer)
    connection_pool.send_welcome_message(writer)

    connection_pool.broadcast_user_join(writer)

    while True:
        try:
            data = await reader.readuntil(b"\n")
        except asyncio.exceptions.IncompleteReadError:
            connection_pool.broadcast_user_quit(writer)
            break

        message = data.decode().strip()

        if message == "/quit":
            connection_pool.broadcast_user_quit(writer)
            break
        elif message == "/list":
            connection_pool.list_users(writer)
        else:
            connection_pool.broadcast_new_message(writer, message)

        await writer.drain()

        if writer.is_closing():
            break

    writer.close()
    await writer.wait_closed()
    connection_pool.remove_user_from_pool(writer)


async def main():
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 8888)

    async with server:
        await server.serve_forever()


connection_pool = ConnectionPool()
asyncio.run(main())
