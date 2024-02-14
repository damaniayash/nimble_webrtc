import pytest
from server import Server
from ball_frames import BallTrack


def test_get_coord():
    ball = BallTrack()
    x, y = ball.get_ball_coord()
    assert isinstance(x, int)
    assert isinstance(y, int)


@pytest.mark.asyncio
async def test_ball_recv():
    """
    Test if BallTrack correctly returns a VideoFrame
    """
    ball = BallTrack()
    frame = await ball.recv()
    assert frame.pts >= 0
    assert frame.to_ndarray().shape[2] == 3


# Need to add tests for signalling
