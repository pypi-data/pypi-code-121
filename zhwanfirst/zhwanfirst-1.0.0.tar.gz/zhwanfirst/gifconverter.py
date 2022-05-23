import glob

from PIL import Image


class GIFConverter:
	def __init__(self, path_in=None, path_out=None, resize=(320, 240)):
		"""
		:param path_in: 원본 여러 이미지 경로 (ex, images/*.png)
		:param path_out: 결과 이미지 경로 (ex, output/filename.gif
		:param resize: 리사이즈 크기 (320, 240
		"""
		self.path_in = path_in or './*.png'
		self.path_out = path_out or './output.gif'
		self.resize = resize

	def convert_gif(self):
		"""
		GIF 이미지 변환 기능 수행
		:return:
		"""
		print(self.path_in, self.path_out, self.resize)
		img, *images = \
			[Image.open(f).resize(self.resize, Image.ANTIALIAS) for f in sorted(glob.glob(self.path_in))]
		try:
			# 이미지 저장
			img.save(fp=self.path_out, format='GIF', append_images=images, save_all=True, duration=200, loop=0)
		except IOError as e:
			print('Cannot convert', e)


if __name__ == '__main__':
	c = GIFConverter(
		'./project/images/*.png',
		'./project/image_out/result.gif'
	)
	c.convert_gif()
	print(GIFConverter.__init__.__doc__, GIFConverter.convert_gif.__doc__)
