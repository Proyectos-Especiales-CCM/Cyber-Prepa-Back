import re
from datetime import timedelta, datetime
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone
from main.views import read_last_lines_from_file
from ..views import send_update_message


class FunctionTests(TestCase):
    def test_send_update_message_success(self):
        # Test if the function does not raise an exception and
        # sends a message to the user with the type of update
        send_update_message("Plays updated", "diego", 1)

        # Test if the function does not raise an exception and
        # sends a message to the user with an unknown type of update
        send_update_message("Unknown update", "diego", 1)

    @override_settings(
        CHANNEL_LAYERS={
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [("unknown", 6379)],
                },
            },
        }
    )
    def test_send_update_message_fail(self):
        # Test if the function raises an exception when the redis
        # server is down and logs the error, but does not raise an
        # exception
        send_update_message("Plays updated", "unknown", 1)
        log_pattern = re.compile(
            r"(?P<level>\w+) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (?P<logger>\w+) (?P<msg>.+)$"
        )
        last_line = read_last_lines_from_file(
            f"{settings.BASE_DIR}/logs/transactions_logs.log", 1
        )
        match = log_pattern.match(last_line[0])
        self.assertEqual(match.group("level"), "ERROR")
        self.assertEqual(
            match.group("msg"),
            "Error sending message to websocket: Error -3 connecting to unknown:6379. -3.",
        )
        # Parse the timestamp from the log
        log_timestamp = datetime.strptime(match.group("timestamp"), '%Y-%m-%d %H:%M:%S,%f')
        log_timestamp = timezone.make_aware(log_timestamp)
        # Assert the timestamp is within the last 5 seconds
        self.assertLessEqual(
            abs(timezone.now() - log_timestamp),
            timedelta(seconds=5)
        )
