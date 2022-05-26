# Builtin modules
import os, unittest, socket
from time import monotonic
# Third party modules
from fsLogger import SimpleLogger, Logger
from fsSignal import Signal, T_Signal
# Local modules
from .. import Client, Request, FEIterator
# Program
class ClientTest(unittest.TestCase):
	signal:T_Signal
	@classmethod
	def setUpClass(cls) -> None:
		if os.environ.get("DEBUG") == "1":
			SimpleLogger("TRACE")
		cls.signal = Signal()
		return None
	def test_withStatement(self) -> None:
		with Client(log=Logger("test_withStatement.Client")) as fec:
			self.assertIs(type(fec), Client)
			with fec as c:
				obj = c.request("ping")
				self.assertIs(type(obj), Request)
				self.assertEqual(obj.isSuccess(), True)
				self.assertIs(type(obj.get()), int)
	def test_simple(self) -> None:
		with Client(log=Logger("test_simple.Client")) as fec:
			self.assertIs(type(fec), Client)
			obj = fec.request("ping")
			self.assertIs(type(obj), Request)
			self.assertEqual(obj.isSuccess(), True)
			self.assertIs(type(obj.get()), int)
	def test_iterator(self) -> None:
		from itertools import islice
		with Client(log=Logger("test_iterator.Client")) as fec:
			data = [
				('0x01000400000000', '0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'),
				('0x01000400000001', '0x00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048'),
				('0x01000400000002', '0x000000006a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd'),
				('0x01000400000003', '0x0000000082b5015589a3fdf2d4baff403e6f0be035a5d9742c1cae6295464449'),
				('0x01000400000004', '0x000000004ebadb55ee9096c9a2f8880e09da59c0d68b1c228da88e48844a1485'),
				('0x01000400000005', '0x000000009b7262315dbf071787ad3656097b892abffd1f95a1a022f896f533fc'),
				('0x01000400000006', '0x000000003031a0e73735690c5a1ff2a4be82553b2a12b776fbd3a215dc8f778d'),
				('0x01000400000007', '0x0000000071966c2b1d065fd446b1e485b2c9d9594acd2007ccbd5441cfc89444'),
				('0x01000400000008', '0x00000000408c48f847aa786c2268fc3e6ec2af68e8468a34a28c61b7f1de0dc6'),
				('0x01000400000009', '0x000000008d9dc510f23c2657fc4f67bea30078cc05a90eb89e84cc475c080805')
			]
			it = fec.createIterator("iterBlocks", "btc", sortBy="blockheight", chunks=2, bitmask=1)
			self.assertIs(type(it), FEIterator)
			i = 0
			for i, r in islice(enumerate(it), 3):
				self.assertEqual(data[i], r)
			else:
				self.assertGreater(i, 0)
			i = 0
			for i, r in islice(enumerate(it, 3), 1):
				self.assertEqual(data[i], r)
			else:
				self.assertGreater(i, 0)
			#
			it = fec.createIterator("iterBlocks", "btc", sortBy="blockheight", fromKey=data[4][0], chunks=2, bitmask=1)
			i = 0
			for i, r in islice(enumerate(it, 5), 3):
				self.assertEqual(data[i], r)
			else:
				self.assertGreater(i, 0)
			self.assertTrue(it.hasNext())
			self.assertEqual(it.next(), data[8])
			#
			it = fec.createIterator("iterBlocks", "btc", sortBy="blockheight", fromKey=data[0][0], desc=True, chunks=2, bitmask=1)
			self.assertFalse(it.hasNext())
	def test_weakref(self) -> None:
		class Dummy:
			def do(self, c:Client) -> None:
				for i in range(5):
					c.request("ping").get()
		with Client(log=Logger("test_weakref.Client")) as fec:
			objs = [ fec.request("ping") for i in range(5) ]
			for obj in objs:
				obj.get()
			self.assertEqual( 5, len(list(fec.requests.itervaluerefs())) )
			objs.clear()
			self.assertNotEqual( 5, len(list(fec.requests.itervaluerefs())) )
			fec.clear()
			d = Dummy()
			d.do(fec)
			del d
			self.assertEqual( 0, len(list(fec.requests.itervaluerefs())) )
	def test_withoutCompression(self) -> None:
		with Client(log=Logger("test_withoutCompression.Client"), disableCompression=True) as fec:
			objs = [fec.request("ping"), fec.request("ping")]
			for obj in objs:
				self.assertIs(type(obj.get()), int)
	def test_retry(self) -> None:
		with Client(log=Logger("test_retry.Client"), retryCount=2, retryDelay=1, ssl=False) as fec:
			s = monotonic()
			req = fec.request("ping")
			try:
				req.get()
			except:
				pass
			self.assertGreater(monotonic()-s, 1.0)
	@unittest.skipUnless(socket.gethostname() == "fusionsolutions", "This works only on the FS server")
	def test_auth(self) -> None:
		with Client("a344613fe3d9ea517ffa0e89e645cdbc", "417e9e027bcd7efb89d250a7cbf701b4", log=Logger("test_auth.Client")) as fec:
			obj = fec.request("sleepWell", [1])
			if obj.isSuccess():
				self.assertEqual(obj.get(), True)
