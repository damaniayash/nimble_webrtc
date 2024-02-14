import asyncio
import numpy as np
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from ball_frames import BallTrack


class Server:
    """
    Represents the server-side application for tracking a ball's coordinates using WebRTC.

    Attributes:
        None

    Methods:
        run: Establishes a connection, creates a data channel, sends offers, and handles signaling.

    """

    def __init__(self):
        pass

    async def run(self, pc, signaling):
        """
        Run the server application.

        Parameters:
            pc (RTCPeerConnection): The RTCPeerConnection object for WebRTC communication.
            signaling (TcpSocketSignaling): The signaling object for communication.

        Returns:
            None
        """
        balltrack = BallTrack()
        await signaling.connect()
        channel = pc.createDataChannel("coordinates")

        @channel.on("open")
        def on_open():
            """Callback when the data channel is open."""
            channel.send("Connection Open")

        @channel.on("message")
        def on_message(message):
            """Callback when a message is received on the data channel."""
            client_x, client_y = list(map(lambda x: float(x), message.split(",")))
            if 0 < client_x < 900 and 0 < client_y < 600:
                server_x, server_y = balltrack.get_ball_coord()
                error = np.sqrt((server_x - client_x) ** 2 + (server_y - client_y) ** 2)
                print(
                    f"Client: ({client_x}, {client_y}) Server: ({server_x}, {server_y}), Error: {error})"
                )
            else:
                print("Circle not found, skipping frame")
            channel.send("Coordinates received")

        pc.addTrack(balltrack)
        await pc.setLocalDescription(await pc.createOffer())
        await signaling.send(pc.localDescription)

        while True:
            obj = await signaling.receive()

            if isinstance(obj, RTCSessionDescription):
                await pc.setRemoteDescription(obj)

            elif obj is None:
                print("Exiting")
                break


if __name__ == "__main__":
    host, port = "127.0.0.1", 8080
    socket_signaling = TcpSocketSignaling(host, port)
    peer_connection = RTCPeerConnection()
    print(f"Established Socket Signaling at: {host} port: {port}")

    server = Server()
    try:
        asyncio.run(
            server.run(
                pc=peer_connection,
                signaling=socket_signaling,
            )
        )
    except KeyboardInterrupt:
        print("Finished process")
    finally:
        asyncio.run(peer_connection.close())
        asyncio.run(socket_signaling.close())
