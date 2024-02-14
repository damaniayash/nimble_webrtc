import asyncio
import cv2
import numpy as np
import multiprocessing as mp
from aiortc.contrib.signaling import TcpSocketSignaling, BYE
from av import VideoFrame
from aiortc import RTCPeerConnection, RTCSessionDescription


class Client:
    def __init__(
        self,
    ):
        self.x_coord, self.y_coord = mp.Value("d", 0.0), mp.Value("d", 0.0)
        self.frame_queue = mp.Queue()
        self.process_a = mp.Process(target=self.detect_ball, args=())
        self.process_a.start()

    def detect_ball(self):
        """
        This function is responsible for detecting the ball in the frame.
        """
        while True:
            if self.frame_queue:
                try:
                    frame_ff = self.frame_queue.get()
                    gray = cv2.cvtColor(frame_ff, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (9, 9), 2)

                    circles = cv2.HoughCircles(
                        blur,
                        cv2.HOUGH_GRADIENT,
                        dp=1,
                        minDist=50,
                        param1=50,
                        param2=30,
                        minRadius=10,
                        maxRadius=30,
                    )
                    if circles is not None:
                        circles = np.round(circles[0, :]).astype("int")

                        x, y, _ = circles[0]
                        self.x_coord.value = x
                        self.y_coord.value = y
                    else:
                        self.x_coord.value = -1
                        self.y_coord.value = -1
                except:
                    pass
            else:
                self.x_coord.value = -1
                self.y_coord.value = -1

    async def display_ball(self, track):
        """
        This takes in track and displays the ball
        """
        while True:
            try:
                frame = await track.recv()
                frame_arr = frame.to_ndarray(format="bgr24")
                self.frame_queue.put(frame_arr)

                cv2.imshow("Client Window", frame_arr)
                if cv2.waitKey(1) == ord("q"):
                    print("Press cntrl + C to exit")
                    cv2.destroyAllWindows()
                    self.process_a.join()
                    break
            except:
                cv2.destroyAllWindows()
                self.process_a.join()
                return

    async def run(self, pc, signaling):
        """
        Runs the main loop for handling signaling, receiving video tracks, and sending ball coordinates.

        Args:
            pc: RTCPeerConnection object for handling WebRTC communication.
            signaling: Signaling object for communication with the server.
        """

        @pc.on("track")
        async def on_track(track):
            await self.display_ball(track)

        await signaling.connect()

        @pc.on("datachannel")
        def on_datachannel(channel):
            """
            Handles the data channel for sending ball coordinates.

            Args:
                channel: Data channel for communication.
            """

            @channel.on("message")
            def on_message(message):
                channel.send(f"{self.x_coord.value},{self.y_coord.value}")

        while True:
            try:
                obj = await signaling.receive()

                if isinstance(obj, RTCSessionDescription):
                    await pc.setRemoteDescription(obj)
                    await pc.setLocalDescription(await pc.createAnswer())
                    await signaling.send(pc.localDescription)

                elif obj is None:
                    print("Exiting")
                    break
            except:
                pass


if __name__ == "__main__":
    host, port = "127.0.0.1", 8080
    socket_signaling = TcpSocketSignaling(host, port)
    peer_connection = RTCPeerConnection()
    print(f"Established Socket Signaling at: {host} port:  {port}")

    client = Client()
    try:
        asyncio.run(
            client.run(
                pc=peer_connection,
                signaling=socket_signaling,
            )
        )
    except KeyboardInterrupt:
        print("Finished process")
        cv2.destroyAllWindows()
    finally:
        asyncio.run(peer_connection.close())
        asyncio.run(socket_signaling.close())
