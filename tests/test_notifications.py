import asyncio
from datetime import datetime, timezone

import app.services.notification as notif_mod


class FakeNotification:
    def __init__(self, user_id=None, title=None, message=None):
        self.id = None
        self.user_id = user_id
        self.title = title
        self.message = message
        self.is_read = False
        # created_at will be set by FakeDBSession.refresh to a timezone-aware datetime
        self.created_at = None


class FakeDBSession:
    def add(self, obj):
        # noop
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        # emulate DB assigning id and timestamp
        obj.id = 999
        obj.created_at = datetime.now(timezone.utc)


def test_create_in_app_notification_broadcast_and_timestamp():
    broadcasted = []

    async def fake_broadcast(user_id, payload):
        broadcasted.append((user_id, payload))

    # Monkeypatch Notification model and manager.broadcast
    original_notification = getattr(notif_mod, "Notification", None)
    original_broadcast = notif_mod.manager.broadcast
    try:
        notif_mod.Notification = FakeNotification
        notif_mod.manager.broadcast = fake_broadcast

        async def run():
            db = FakeDBSession()
            # call the synchronous factory inside an event loop so it will schedule the async broadcast
            notif = notif_mod.create_in_app_notification(db, user_id=123, title="T", message="M", background_tasks=None)

            # allow scheduled tasks to run
            await asyncio.sleep(0.1)

            assert notif is not None
            assert notif.id == 999
            assert len(broadcasted) >= 1
            user_id, payload = broadcasted[0]
            assert user_id == 123
            assert payload["id"] == 999
            # created_at should be an ISO string with timezone info
            ts = datetime.fromisoformat(payload["created_at"])
            assert ts.tzinfo is not None

        asyncio.run(run())
    finally:
        if original_notification is not None:
            notif_mod.Notification = original_notification
        notif_mod.manager.broadcast = original_broadcast
