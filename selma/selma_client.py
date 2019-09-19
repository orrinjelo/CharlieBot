import asyncio
import logging

logger = logging.getLogger('discord')

class Client(object):
    def __init__(self, username, password=None, addr='localhost', port=7777):
        self.u = username
        self.p = password
        self.addr = addr
        self.port = port

    async def connect(self, handler_cb):
        self.r, self.w = await asyncio.open_connection(self.addr, self.port)
        self.cb = handler_cb

        if self.p:
            self.request('connect {} {}'.format(self.u, self.p))
        else:
            self.request('connect {}'.format(self.u))

        while True:
            msg = await self.r.readline()
            if msg.strip() is None:
                await asyncio.sleep(1)
                continue
            await self.handle_msg(msg)

    async def request(self, msg):
        self.writer.write(bytes(msg + '\n'))
        logger.debug('Writing: {}'.format(msg))

    async def handle_msg(self, msg):
        '''Eventually add handling of images, links, custom formatting, etc.
        For now, just return the message.'''
        await self.cb(msg.strip().decode('utf-8'))
        logger.debug('{}'.format(msg.strip().decode('utf-8')))

if __name__ == '__main__':
    h = Client('wizard', lambda x: print(x))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(h.connect())
    loop.close()