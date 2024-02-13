import cv2
import numpy as np
from av import VideoFrame
from aiortc import VideoStreamTrack


class BallTrack(VideoStreamTrack):
    """
    A class representing a simple ball tracking video stream track.

    Attributes:
    - width (int): Width of the video frame.
    - height (int): Height of the video frame.
    - ball_radius (int): Radius of the ball.
    - ball_color (tuple): Color of the ball in BGR format.
    - ball_x (int): X-coordinate of the ball's current position.
    - ball_y (int): Y-coordinate of the ball's current position.
    - ball_velocity_x (int): Velocity of the ball in the x-direction.
    - ball_velocity_y (int): Velocity of the ball in the y-direction.
    """

    def __init__(self):
        """
        Initialize the BallTrack object.

        Sets up initial parameters for the ball and video frame.
        """
        super().__init__()  # don't forget this!

        self.width = 900
        self.height = 600
        self.ball_radius = 20
        self.ball_color = (128, 255, 128)
        self.ball_x = np.random.randint(self.ball_radius, self.width - self.ball_radius)
        self.ball_y = np.random.randint(
            self.ball_radius, self.height - self.ball_radius
        )
        self.ball_velocity_x = 15
        self.ball_velocity_y = 15

    def get_ball_coord(self):
        """
        Get the current coordinates of the ball.

        Returns:
        - tuple: Tuple containing the x and y coordinates of the ball.
        """
        return self.ball_x, self.ball_y

    async def recv(self):
        """
        Receive the next video frame with the updated ball position.

        Returns:
        - VideoFrame: A video frame with the drawn ball at its new position.
        """
        pts, time_base = await self.next_timestamp()
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8)

        # Update the ball position
        self.ball_x += self.ball_velocity_x
        self.ball_y += self.ball_velocity_y

        # Check collision
        if (
            self.ball_x < self.ball_radius
            or self.ball_x > self.width - self.ball_radius
        ):
            self.ball_velocity_x = -self.ball_velocity_x
        if (
            self.ball_y < self.ball_radius
            or self.ball_y > self.height - self.ball_radius
        ):
            self.ball_velocity_y = -self.ball_velocity_y

        # Place the ball
        cv2.circle(
            frame,
            (int(self.ball_x), int(self.ball_y)),
            self.ball_radius,
            self.ball_color,
            -1,
        )

        frame = VideoFrame.from_ndarray(frame, format="bgr24")

        frame.pts = pts
        frame.time_base = time_base

        return frame
