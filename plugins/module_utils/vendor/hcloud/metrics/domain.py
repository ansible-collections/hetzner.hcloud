from __future__ import annotations

from datetime import datetime
from typing import Literal

try:
    from dateutil.parser import isoparse
except ImportError:
    isoparse = None

from ..core import BaseDomain

TimeSeries = dict[str, dict[Literal["values"], list[tuple[float, str]]]]


class Metrics(BaseDomain):
    """Metrics Domain

    :param start: Start of period of metrics reported.
    :param end: End of period of metrics reported.
    :param step: Resolution of results in seconds.
    :param time_series: Dict with time series data, using the name of the time series as
        key. The metrics timestamps and values are stored in a list of tuples
        ``[(timestamp, value), ...]``.
    """

    start: datetime
    end: datetime
    step: float
    time_series: TimeSeries

    __api_properties__ = (
        "start",
        "end",
        "step",
        "time_series",
    )
    __slots__ = __api_properties__

    def __init__(
        self,
        start: str,
        end: str,
        step: float,
        time_series: TimeSeries,
    ):
        self.start = isoparse(start)
        self.end = isoparse(end)
        self.step = step
        self.time_series = time_series
