from abc import ABC
from typing import Iterable, Iterator, TYPE_CHECKING
from typing import List, Any, Tuple

import numpy as np
import tensorflow as tf




class DataGenerator(object):
    """数据生成器模版
    """
    def __init__(self, data, batch_size=32, buffer_size=None):
        self.data = data
        self.batch_size = batch_size
        if hasattr(self.data, '__len__'):
            self.steps = len(self.data) // self.batch_size
            if len(self.data) % self.batch_size != 0:
                self.steps += 1
        else:
            self.steps = None
        self.buffer_size = buffer_size or batch_size * 1000

    def __len__(self):
        return self.steps

    def sample(self, random=False):
        """
            采样函数，每个样本同时返回一个is_end标记
        """
        if random:
            if self.steps is None:
                def generator():
                    caches, isfull = [], False
                    for d in self.data:
                        caches.append(d)
                        if isfull:
                            i = np.random.randint(len(caches))
                            yield caches.pop(i)
                        elif len(caches) == self.buffer_size:
                            isfull = True
                    while caches:
                        i = np.random.randint(len(caches))
                        yield caches.pop(i)
            else:
                def generator():
                    for i in np.random.permutation(len(self.data)):
                        yield self.data[i]
            data = generator()
        else:
            data = iter(self.data)
        d_current = next(data)
        for d_next in data:
            yield False, d_current
            d_current = d_next
        yield True,d_current

    def __iter__(self, random=False):
        raise NotImplementedError

    def forfit(self, random=False):
        while True:
            for d in self.__iter__(random):
                yield d

    def to_dataset(self, types, shapes, names=None, padded_batch=False):
        """转为tf.data.Dataset格式
        如果传入names的话，自动把数据包装成dict形式。
        """
        if names is None:

            generator = self.forfit

        else:

            if type(names) == str:
                warps = lambda k, v: {k: v}
            elif type(names[0]) == str:
                warps = lambda k, v: dict(zip(k, v))
            else:
                warps = lambda k, v: tuple(
                    dict(zip(i, j)) for i, j in zip(k, v)
                )

            def generator():
                for d in self.forfit():
                    yield warps(names, d)

            types = warps(names, types)
            shapes = warps(names, shapes)

        if padded_batch:
            dataset = tf.data.Dataset.from_generator(
                generator, output_types=types
            )
            dataset = dataset.padded_batch(self.batch_size, shapes)
        else:
            dataset = tf.data.Dataset.from_generator(
                generator, output_types=types, output_shapes=shapes
            )
            dataset = dataset.batch(self.batch_size)

        return dataset


class ABCGenerator(Iterable, ABC):
    def __init__(self, buffer_size: int = 2000) -> None:
        self.buffer_size = buffer_size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def sample(self) -> Iterator[Tuple[Any, Any]]:
        buffer, is_full = [], False
        for sample in self:
            buffer.append(sample)
            if is_full:
                i = np.random.randint(len(buffer))
                yield buffer.pop(i)
            elif len(buffer) == self.buffer_size:
                is_full = True
        while buffer:
            i = np.random.randint(len(buffer))
            yield buffer.pop(i)


class CorpusGenerator(ABCGenerator):

    def __init__(self,
                 x_data: List,
                 y_data: List,
                 *,
                 buffer_size: int = 2000) -> None:
        super(CorpusGenerator, self).__init__(buffer_size=buffer_size)
        self.x_data = x_data
        self.y_data = y_data
        self.buffer_size = buffer_size

    def __iter__(self) -> Iterator[Tuple[Any, Any]]:
        for i in range(len(self.x_data)):
            yield self.x_data[i], self.y_data[i]

    def __len__(self) -> int:
        return len(self.x_data)




class BatchGenerator(DataGenerator):
    """数据生成器
    """
    def __init__(self,data,text_processor,label_processor,seq_length=None,batch_size=64, buffer_size=None,use_rdrop=True):
        super(BatchGenerator,self).__init__(data,batch_size,buffer_size)
        self.text_processor = text_processor
        self.label_processor = label_processor
        self.seq_length = seq_length
        self.use_rdrop = use_rdrop


    def __iter__(self, random=False):
        batch_x, batch_y = [], []
        for is_end,(x, y) in self.sample(random):
            if self.use_rdrop:
                batch_size = self.batch_size * 2
                for i in range(2):
                    batch_x.append(x)
                    batch_y.append(y)
            else:
                batch_x.append(x)
                batch_y.append(y)
                batch_size = self.batch_size


            if len(batch_x) == batch_size  or is_end:
                x_tensor = self.text_processor.transform(batch_x,seq_length=self.seq_length)
                max_sequence_len = x_tensor[0].shape[1]
                if self.seq_length:
                    max_sequence_len = self.seq_length

                y_tensor = self.label_processor.transform(batch_y,
                                                          seq_length=max_sequence_len)
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []




class GlobalPointGenerator(DataGenerator):
    """数据生成器
    """
    def __init__(self,data,text_processor,label_processor,seq_length=None,batch_size=64, buffer_size=None,use_rdrop=True):
        super(GlobalPointGenerator,self).__init__(data,batch_size,buffer_size)
        self.text_processor = text_processor
        self.label_processor = label_processor
        self.seq_length = seq_length

    def __iter__(self, random=False):
        batch_x, batch_y = [], []
        for (x, y) in self.sample():
            batch_x.append(x)
            batch_y.append(y)
            if len(batch_x) == self.batch_size :
                x_tensor = self.text_processor.transform(batch_x,
                                                         seq_length=self.seq_length,
                                                         )
                # x_tensor [x_token, segment]
                max_sequence_len = x_tensor[0].shape[1]
                if self.seq_length:
                    max_sequence_len = self.seq_length

                y_tensor = self.label_processor.transform(batch_y,
                                                          seq_length=max_sequence_len)
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []
        if batch_x:
            x_tensor = self.text_processor.transform(batch_x,
                                                     seq_length=self.seq_length,
                                                     )
            # x_tensor [x_token, segment]
            max_sequence_len = x_tensor[0].shape[1]
            if self.seq_length:
                max_sequence_len = self.seq_length

            y_tensor = self.label_processor.transform(batch_y,
                                                      seq_length=max_sequence_len)
            yield x_tensor, y_tensor







class BertGeneratorDataSet(Iterable):
    '''
    BERT generator data
    '''
    def __init__(self,
                 corpus: CorpusGenerator,
                 *,
                 batch_size: int = 64,
                 seq_length: int = None,
                 max_position: int = None,
                 segment: bool = True,
                 text_processor: 'ABCProcessor'):
        self.corpus = corpus

        self.text_processor = text_processor
        self.seq_length = seq_length
        self.max_position = max_position
        self.segment = segment
        self.batch_size = batch_size

    def __len__(self) -> int:
        return max(len(self.corpus) // self.batch_size, 1)

    def __iter__(self) -> Iterator:
        batch_x = []
        for x, y in self.corpus.sample():
            if y:
                batch_x.append((x,y))
            else:
                batch_x.append(x)
            if len(batch_x) == self.batch_size:
                x_tensor = self.text_processor.transform(batch_x,
                                                            seq_length=self.seq_length,
                                                            segment=self.segment)

                yield x_tensor,None
                batch_x = []

    def take(self, batch_count: int = None) -> Any:
        # x_shape = [2,self.batch_size, self.seq_length]
        # dataset = tf.data.Dataset.from_generator(self.__iter__,
        #                                          output_types=(tf.int64)
        #                                          )
        # dataset = dataset.repeat()
        # dataset = dataset.prefetch(50)
        # if batch_count is None:
        #     batch_count = len(self)
        # return dataset.take(batch_count)
        while True:
            for d in self.__iter__():
                yield d



class EncoderGenerator(DataGenerator):
    """数据生成器
    """
    def __init__(self,data,text_processor,label_processor,seq_length=None,batch_size=64, buffer_size=None,use_rdrop=True):
        super(EncoderGenerator,self).__init__(data,batch_size,buffer_size)
        self.text_processor = text_processor
        self.label_processor = label_processor
        self.seq_length = seq_length
        self.use_rdrop = use_rdrop


    def __iter__(self, random=False):
        batch_x, batch_y = [], []
        for is_end,(x, y) in self.sample(random):
            if type(x) != list:
                assert TypeError("x输入格式错误")
            batch_x.extend(x)
            batch_y.extend(len(x) * [y])


            if len(batch_x) == self.batch_size  or is_end:
                x_tensor = self.text_processor.transform(batch_x,seq_length=self.seq_length)
                max_sequence_len = x_tensor[0].shape[1]
                if self.seq_length:
                    max_sequence_len = self.seq_length

                y_tensor = self.label_processor.transform(batch_y,
                                                          seq_length=max_sequence_len)
                yield x_tensor, y_tensor
                batch_x, batch_y = [], []
