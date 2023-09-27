from datetime import datetime
from typing import Dict

from croniter import croniter
from dateutil import rrule

from sentry.monitors.types import IntervalUnit, ScheduleConfig

SCHEDULE_INTERVAL_MAP: Dict[IntervalUnit, int] = {
    "year": rrule.YEARLY,
    "month": rrule.MONTHLY,
    "week": rrule.WEEKLY,
    "day": rrule.DAILY,
    "hour": rrule.HOURLY,
    "minute": rrule.MINUTELY,
}


def get_next_schedule(
    reference_ts: datetime,
    schedule: ScheduleConfig,
):
    """
    Given the schedule type and schedule, determine the next timestamp for a
    schedule from the reference_ts

    Examples:

    >>> get_next_schedule('05:30', CrontabSchedule('0 * * * *'))
    >>> 06:00

    >>> get_next_schedule('05:30', CrontabSchedule('30 * * * *'))
    >>> 06:30

    >>> get_next_schedule('05:35', IntervalSchedule(interval=2, unit='hour'))
    >>> 07:35
    """
    # Ensure we clamp the expected time down to the minute, that is the level
    # of granularity we're able to support

    if schedule.type == "crontab":
        iterator = croniter(schedule.crontab, reference_ts)
        return iterator.get_next(datetime).replace(second=0, microsecond=0)

    if schedule.type == "interval":
        rule = rrule.rrule(
            freq=SCHEDULE_INTERVAL_MAP[schedule.unit],
            interval=schedule.interval,
            dtstart=reference_ts,
            count=2,
        )
        return rule.after(reference_ts).replace(second=0, microsecond=0)

    raise NotImplementedError("unknown schedule_type")
