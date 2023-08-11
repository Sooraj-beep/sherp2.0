import os, aiohttp


async def save_attachment(attachment):
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as response:
            if response.status != 200:
                return -1
            filename = os.path.join(
                "attachments", attachment.filename
            )  # save to ./attachments
            with open(filename, "wb") as f:
                f.write(await response.read())
            return filename
