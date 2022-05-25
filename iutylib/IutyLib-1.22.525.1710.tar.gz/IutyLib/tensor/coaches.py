import os,math,time
import random
import numpy as np
import tensorflow as tf
import tensor.lays as lays
import tensor.outputs


class CNNCoach:
	ImgW = 64
	ImgH = 64
	
	Ratio = 0.3
	Capacity = 200
	BatchSize = 20
	OutPutStep = 10
	MaxOutPut = 10000000
	LearningRate = 0.000015
	
	ModelTag = 'Reserve' + '\\'
	
	Tag_True_Path = []
	Tag_False_Path = []
	Tag_Test_Path = []
	
	DataSource = []
	LabelSource = []
	
	_running = False
	
	def __init__(self,projectname,projectpath,modeltag = None):
		self.Name = projectname
		self.ProjectPath = projectpath
		if not modeltag is None:
			self.ModelTag = modeltag
		
		pass
	
	def setCoach(self,**kwargs):
		if 'ModelTag' in kwargs:
			self.ModelTag = kwargs['ModelTag']
		if 'ImgW' in kwargs:
			self.ImgW = kwargs['ImgW']
		if 'ImgH' in kwargs:
			self.ImgH = kwargs['ImgH']
		if 'Ratio' in kwargs:
			self.Ratio = kwargs['Ratio']
		if 'Capacity' in kwargs:
			self.Capacity = kwargs['Capacity']
		if 'TrainBatchSize' in kwargs:
			self.TrainBatchSize = kwargs['TrainBatchSize']
		if 'TestBatchSize' in kwargs:
			self.TestBatchSize = kwargs['TestBatchSize']
		if 'OutPutStep' in kwargs:
			self.OutPutStep = kwargs['OutPutStep']
		if 'MaxOutPut' in kwargs:
			self.MaxOutPut = kwargs['MaxOutPut']
		if 'LearningRate' in kwargs:
			self.LearningRate = kwargs['LearningRate']
		pass
	
	def setData(self,imgs):
		self.Tag_True_Path.clear()
		self.Tag_False_Path.clear()
		self.Tag_Test_Path.clear()
		
		if 'True' in imgs:
			self.Tag_True_Path += imgs['True']
		if 'False' in imgs:
			self.Tag_False_Path += imgs['False']
		if 'Test' in imgs:
			self.Tag_Test_Path += imgs['Test']
		pass
	
	def getDataFromPath(self,path,label):
		imgnames = os.listdir(path)
		imgs = []
		labels = []
		for imgname in imgnames:
			imgpath = os.path.join(path,imgname)
			imgs.append(imgpath)
			labels.append(label)
		return imgs,labels
		
	def getDataSource(self):
		self.DataSource.clear()
		self.LabelSource.clear()
		for dir in self.Tag_True_Path:
			imgs,labels = self.getDataFromPath(dir,1)
			self.DataSource += imgs
			self.LabelSource += labels
		
		for dir in self.Tag_False_Path:
			imgs,labels = self.getDataFromPath(dir,0)
			self.DataSource += imgs
			self.LabelSource += labels
		pass
	
	def getInput(self,reload = False):
		#step0:reload
		if (reload):
			self.getDataSource()
			
		#step1:读取文件和标签
		if len(self.DataSource) == 0:
			self.getDataSource()
		
		#step2:图片和标签做打乱处理,区分训练集和测试集
		'''
		tra_imgs = []
		tra_labs = []
		val_imgs = []
		val_labs = []
			
		for i in range(self.BatchSize):
			index = random.randint(0,len(self.DataSource))
			tra_imgs.append(self.DataSource[index])
			tra_labs.append(self.LabelSource[index])
		for i in range(self.BatchSize):
			index = random.randint(0,len(self.DataSource))
			val_imgs.append(self.DataSource[index])
			val_labs.append(self.LabelSource[index])
		'''
		temp = np.array([self.DataSource, self.LabelSource])
		temp = temp.transpose()
		np.random.shuffle(temp)
		all_image_list = list(temp[:, 0])
		all_label_list = list(temp[:, 1])
		
		n_sample = len(all_label_list)
		n_val = int(math.ceil(n_sample * 0.1))  # 测试样本数
		n_train = n_sample - n_val  # 训练样本数

		tra_images = all_image_list[0:n_train]
		tra_labels = all_label_list[0:n_train]
		tra_labels = [int(float(i)) for i in tra_labels]
		val_images = all_image_list[n_train:-1]
		val_labels = all_label_list[n_train:-1]
		val_labels = [int(float(i)) for i in val_labels]
		print('tra:{},val:{}'.format(len(tra_labels),len(val_labels)))
		return tra_images, tra_labels, val_images, val_labels
	
	def getBatch(self,image,label,batch_size):
		image = tf.cast(image, tf.string)
		label = tf.cast(label, tf.int32)
		
		input_queue = tf.train.slice_input_producer([image, label])
		label = input_queue[1]
		image_contents = tf.read_file(input_queue[0])  # read img from a queue
		
		# step2：将图像解码，不同类型的图像不能混在一起，要么只用jpeg，要么只用png等。
		image = tf.image.decode_jpeg(image_contents, channels=3)
		
		# step3：数据预处理，对图像进行旋转、缩放、裁剪、归一化等操作，让计算出的模型更健壮。
		image = tf.image.resize_image_with_crop_or_pad(image, self.ImgW, self.ImgH)
		image = tf.image.per_image_standardization(image)
		
		# step4：生成batch
		# image_batch: 4D tensor [batch_size, width, height, 3],dtype=tf.float32
		# label_batch: 1D tensor [batch_size], dtype=tf.int32
		image_batch, label_batch = tf.train.batch([image, label],batch_size=batch_size,num_threads=32,capacity=self.Capacity)
		label_batch = tf.reshape(label_batch, [batch_size])
		image_batch = tf.cast(image_batch, tf.float32)
		return image_batch,label_batch
	
	def initSession(self):
		summary_op = tf.summary.merge_all()
		sess = tf.Session()
		sess.run(tf.global_variables_initializer())
		return sess
		
	
	def getLogits(self,inputs,batch_size):
		conv1 = lays.getConv('conv1',inputs,64)
		pool1 = lays.getPool('pool1',conv1,0)
		conv2 = lays.getConv('conv2',pool1,16)
		pool2 = lays.getPool('pool2',conv2,0)
		local1 = lays.getLocal('local1',pool2,128)
		local2 = lays.getLocal('local2',local1,128)
		logits = lays.getLinear('linear',local2,2)
		
		return logits
		#return tensor.model.inference(inputs,batch_size)
	
	def getLosses(self,logits,label_batch):
		return tensor.outputs.losses(logits,label_batch)
		#return tensor.model.losses(logits,label_batch)
	
	def getTrainning(self,loss,learning_rate):
		return tensor.outputs.trainning(loss,learning_rate)
	
	def getEvaluation(self,logits,label_batch):
		return tensor.outputs.evaluation(logits,label_batch)
	
	def doTrain(self):
		tra_imgs, tra_labs, val_imgs, val_labs = self.getInput()
		
		tra_img_batch,tra_lab_batch = self.getBatch(tra_imgs,tra_labs,self.BatchSize)
		val_img_batch,val_lab_batch = self.getBatch(val_imgs,val_labs,self.BatchSize)
		
		tra_logits = self.getLogits(tra_img_batch,self.BatchSize)
		print(tra_logits)
		tra_loss = self.getLosses(tra_logits,tra_lab_batch)
		op = self.getTrainning(tra_loss,self.LearningRate)
		tra_acc = self.getEvaluation(tra_logits,tra_lab_batch)
		
		val_logits = self.getLogits(val_img_batch,self.BatchSize)
		val_loss = self.getLosses(val_logits,tra_lab_batch)
		val_acc = self.getEvaluation(val_logits,val_lab_batch)
		self.sess = self.initSession()
		saver = tf.train.Saver()
		savedir = self.ProjectPath + self.ModelTag
		if 'checkpoint' in os.listdir(savedir):
			modelpath = tf.train.latest_checkpoint(savedir)
			saver.restore(self.sess,modelpath)
			step = int(modelpath.split('-')[-1])
		else:
			step = 0
		
		coord = tf.train.Coordinator()
		threads = tf.train.start_queue_runners(sess=self.sess, coord=coord)
		i = 0
		ts = time.time()
		self._running = True
		while 1:
			
			i+=1
			_, r_tra_loss, r_tra_acc, r_val_acc = self.sess.run([op, tra_loss, tra_acc,val_acc])
			#_, r_tra_loss, r_tra_acc = self.sess.run([op, tra_loss, tra_acc])
			if i%self.OutPutStep == 0:
				step += 1
				te = time.time()
				print('Step %d, train loss = %.2f, train accuracy = %.2f%%, test accuracy = %.2f%%,spend = %.2fs/step' % (step*self.OutPutStep, r_tra_loss, r_tra_acc * 100.0, r_val_acc * 100.0,(te-ts)/self.OutPutStep))
				#print('Step %d, train loss = %.2f, train accuracy = %.2f%%, test accuracy = %.2f%%' % (step*self.OutPutStep, r_tra_loss, r_tra_acc * 100.0))
				checkpoint_path = os.path.join(savedir, 'model.ckpt')
				saver.save(self.sess, checkpoint_path, global_step=step)
				ts = time.time()
			if i>self.OutPutStep*self.MaxOutPut:
				break
			
			if not self._running:
				break
		
		pass
	
