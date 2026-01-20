import asyncio
import logging
from typing import Dict, List
from asyncio import Queue

logger = logging.getLogger(__name__)

# Tunables
MAX_QUEUE_SIZE = 100
MAX_CONNECTIONS_PER_USER = 6


class NotificationManager:
    def __init__(self):
        # Maps user_id to a list of active connection queues
        self.active_connections: Dict[int, List[Queue]] = {}

    async def connect(self, user_id: int) -> Queue:
        """
        Create a new bounded queue for a connecting user and return it.
        If too many connections exist for a user, drop the oldest.
        """
        queue: Queue = Queue(maxsize=MAX_QUEUE_SIZE)
        conns = self.active_connections.setdefault(user_id, [])
        # Enforce max connections per user
        if len(conns) >= MAX_CONNECTIONS_PER_USER:
            # Drop oldest connection (best-effort)
            old_queue = conns.pop(0)
            try:
                # put a sentinel to encourage disconnect
                old_queue.put_nowait({"type": "server_disconnect", "reason": "too_many_connections"})
            except Exception:
                pass

        conns.append(queue)
        logger.info(f"User {user_id} connected to SSE. Active connections: {len(conns)}")
        return queue

    async def disconnect(self, user_id: int, queue: Queue):
        """
        Remove a queue from the user's active connections.
        """
        conns = self.active_connections.get(user_id)
        if not conns:
            return
        if queue in conns:
            try:
                conns.remove(queue)
            except ValueError:
                pass

        if not conns:
            self.active_connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected from SSE. Remaining connections: {len(self.active_connections.get(user_id, []))}")

    async def broadcast(self, user_id: int, message: dict):
        """
        Push a message to all active connections for a specific user.
        This is non-blocking: if a queue is full we drop the oldest item.
        """
        conns = self.active_connections.get(user_id)
        if not conns:
            return

        for queue in list(conns):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # Drop one item then try again (make space)
                try:
                    _ = queue.get_nowait()
                except Exception:
                    pass
                try:
                    queue.put_nowait(message)
                except Exception:
                    logger.warning(f"Dropping message for user {user_id} due to full queue")
        logger.debug(f"Broadcasted SSE message to user {user_id} on {len(conns)} connections")


# Global instance
manager = NotificationManager()
