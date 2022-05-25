from nehushtan.socket.wormhole.NehushtanWormhole import NehushtanWormhole

if __name__ == '__main__':
    wormhole = NehushtanWormhole(7090, '116.62.78.192', 20000, r"/Users/leqee/code/nehushtan/log")
    wormhole.run()
