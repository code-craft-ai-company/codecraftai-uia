"""
    .. module:: fakeclock
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A controllable stand-in for the ``time`` module used by polling code.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List


class FakeClock:
    """
        A clock whose ``sleep`` advances ``time`` instantly.

        Product code that polls with ``time.sleep`` and checks deadlines with
        ``time.time`` runs against this object in no wall-clock time, and every
        sleep it asked for is recorded so a test can assert on the polling
        cadence.
    """

    def __init__(self, start: float = 1000.0):
        self._now = start
        self._sleeps: List[float] = []
        return

    @property
    def now(self) -> float:
        """
            The current fake time in seconds.
        """
        return self._now

    @property
    def sleeps(self) -> List[float]:
        """
            Every duration passed to :meth:`sleep`, in call order.
        """
        return self._sleeps

    def time(self) -> float:
        """
            Returns the current fake time, mirroring ``time.time``.
        """
        rtnval = self._now
        return rtnval

    def sleep(self, seconds: float) -> None:
        """
            Advances the clock by ``seconds`` instead of blocking, mirroring ``time.sleep``.

            :param seconds: The duration the caller wanted to wait.
        """
        self._sleeps.append(seconds)
        self._now = self._now + seconds
        return
