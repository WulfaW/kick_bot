import asyncio
import aiohttp

async def test_peak():
    url = "https://api.henrikdev.xyz/valorant/v2/mmr/eu/jeno/0612"
    headers = {"Authorization": "HDEV-b4c4f685-997b-4272-b41f-265dc6452c9e"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            print(data.get("data", {}).get("highest_rank"))

if __name__ == "__main__":
    asyncio.run(test_peak())
