import asyncio
import importlib

from app.core.sse import NotificationManager
import app.core.sse as sse_module


def test_connect_broadcast_disconnect():
    async def run():
        mgr = NotificationManager()
        q1 = await mgr.connect(1)
        q2 = await mgr.connect(1)

        await mgr.broadcast(1, {"msg": "hello"})

        msg1 = await asyncio.wait_for(q1.get(), timeout=1.0)
        msg2 = await asyncio.wait_for(q2.get(), timeout=1.0)

        assert msg1 == {"msg": "hello"}
        assert msg2 == {"msg": "hello"}

        await mgr.disconnect(1, q1)
        await mgr.disconnect(1, q2)
        assert 1 not in mgr.active_connections

    asyncio.run(run())


def test_max_connections_eviction():
    async def run():
        # Temporarily reduce max connections to exercise eviction
        old_max = sse_module.MAX_CONNECTIONS_PER_USER
        sse_module.MAX_CONNECTIONS_PER_USER = 2
        try:
            mgr = NotificationManager()
            q1 = await mgr.connect(2)
            q2 = await mgr.connect(2)
            q3 = await mgr.connect(2)

            # Oldest should have been evicted so we have at most 2 connections
            assert len(mgr.active_connections.get(2, [])) == 2

            # Broadcast should succeed to remaining connections
            await mgr.broadcast(2, {"ping": "pong"})
            # Drain remaining queues
            conns = mgr.active_connections.get(2, [])
            results = []
            for q in conns:
                results.append(await asyncio.wait_for(q.get(), timeout=1.0))
            assert {"ping": "pong"} in results

            # cleanup
            for q in list(conns):
                await mgr.disconnect(2, q)
        finally:
            sse_module.MAX_CONNECTIONS_PER_USER = old_max

    asyncio.run(run())
