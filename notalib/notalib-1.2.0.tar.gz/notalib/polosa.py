from contextlib import contextmanager
from datetime import datetime, timedelta


# Так, сейчас будет реклама.
# Тебе случалось когда-нибудь обрабатывать большие, ну, массивы каких-то данных или элементов?
# Не по объёму, а количество большое.
# Ну, у меня вот всё время на работе бывает надо обработать сто тыщ строк или миллион.
# Естественно, это занимает кучу времени, поэтому я хочу в процессе видеть, сколько там есть и сколько осталось.
# То есть обычно всё начинается с того, я пишу print(id).
# Потом мне хочется ещё видеть, сколько их там всего, и тогда я пишу print(id, total).
# Потом я понимаю, что у меня вообще-то консоль не только для миллиона id, там вообще-то другие полезные штуки бывают, и я начинаю добавлять \r в конце этих строк, чтоб оно на одном месте было.
# Потом я понимаю, что пришла пора оптимизаций и неплохо бы ещё считать, сколько фиговин в секунду оно успевает делать, поэтому я ещё отмечаю начальное время и каждый раз делю количество на прошедшее время.
# А потом понимаю, что консоль медленная и сам вывод этой херни замедляет процесс, и неплохо бы ещё сделать так, чтобы прогресс обновлялся только раз в ~100 мс.
# Последний раз у меня такой маленький сниппет разросся до 30 строк. Бывало такое?
# Ну а теперь реклама!
# https://asciinema.org/a/UI1aOqjQC1KXx303kaVGrxjQp


# print('==> Doing important stuff...')
# N = 2_000_000
# with polosa(total=N) as p:
# 	for i in range(0, N):
# 		p.tick(i+1, f'real index is {i}')
#		# or
#		#p.tick(caption=f'real index is {i}')
#		# or even
#		#p.tick()
# print('==> All done!')


class _Polosa:
	def __init__(self, total=None, throttle_ms=200):
		self.start = datetime.now()
		self.last_update = None
		self.last_num = 0
		self.throttle_ms = throttle_ms
		self.total = total
		self.buf = ''

	def tick(self, num=None, caption=''):
		now = datetime.now()

		if num == None:
			self.last_num += 1
			num = self.last_num

		self.buf = f'{num}'
		if self.total != None:
			self.buf += f'/{self.total}'
		per_sec = num / (now - self.start).total_seconds()
		self.buf += f'   {per_sec:.1f}/sec   {caption}'

		if (self.last_update != None) and (now - self.last_update < timedelta(milliseconds=self.throttle_ms)):
			return

		print(self.buf, end='   \r')
		self.last_update = now

	def _finalize(self):
		print(self.buf)


@contextmanager
def polosa(*args, **kwargs):
	p = _Polosa(*args, **kwargs)
	try:
		yield p
	finally:
		p._finalize()

