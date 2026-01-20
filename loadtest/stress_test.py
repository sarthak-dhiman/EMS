import argparse
import asyncio
import time
import httpx

async def worker(name, client, url, sem, counter, total):
    while True:
        async with sem:
            i = next(counter)
            if i > total:
                return
            try:
                resp = await client.get(url)
                print(f"[{name}] {i}: {resp.status_code} in {resp.elapsed.total_seconds():.3f}s")
            except Exception as e:
                print(f"[{name}] {i}: error {e}")

def counter_gen():
    n = 1
    while True:
        yield n
        n += 1

async def run(url, concurrency, total):
    sem = asyncio.Semaphore(concurrency)
    gen = counter_gen()
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [asyncio.create_task(worker(f"w{i}", client, url, sem, gen, total)) for i in range(concurrency)]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=False, default='http://localhost:8000/', help='Target URL')
    p.add_argument('--concurrency', type=int, default=20)
    p.add_argument('--requests', type=int, default=200)
    args = p.parse_args()
    total = args.requests
    start = time.time()
    try:
        asyncio.run(run(args.url, args.concurrency, total))
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        print('Done in', time.time()-start)
