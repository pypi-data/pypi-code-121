"""
LeNet backbone implementation derived from [Backpropagation Applied to Handwritten Zip Code Recognition](https://direct.mit.edu/neco/article-abstract/1/4/541/5515/Backpropagation-Applied-to-Handwritten-Zip-Code?redirectedFrom=fulltext)
"""
from functools import partial
from typing import List
from typing_extensions import Literal
from pydantic import Field
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Conv2D
from tensorflow.keras import layers

from brevettiai.model.factory import ModelFactory


class LeNetSegmentationBackbone(ModelFactory):
    output_layers: List[str]
    layers: int = 3
    filters: int = 8
    filter_bank_multiplier: float = 2.0
    activation: str = Field(default="relu")
    pooling: Literal["AvgPool2D", "MaxPool2D"] = Field(default="MaxPool2D")
    padding: Literal["SAME", "VALID"] = Field(default="SAME")
    kernel_size: List = Field(default=[3, 3], description="Kernel size for convolutional kernels")

    def build(self, input_shape, *args, **kwargs):
        backbone = Sequential(name="BaseLeNetBackbone")
        pooling_factory = lambda : getattr(layers, self.pooling)

        filters = self.filters
        backbone.add(Conv2D(filters, self.kernel_size, 1,
                            input_shape=input_shape,
                            activation=self.activation,
                            name="conv2d_1",
                            padding=self.padding))

        for layer in range(1, self.layers):
            filters = int(filters * self.filter_bank_multiplier)
            backbone.add(pooling_factory()((2, 2), name=f"{self.pooling.lower()}_{layer}"))
            backbone.add(Conv2D(filters, self.kernel_size, 1, activation=self.activation, name=f"conv2d_{layer + 1}",
                                padding=self.padding))

        backbone = Model(backbone.input, [backbone.get_layer(l).output for l in self.output_layers],
                                  name="LeNetBackbone")

        return backbone


lenet_backbone = partial(
    LeNetSegmentationBackbone,
    layers=6,
    filter_bank_multiplier=1.5,
    padding="VALID",
    output_layers=['conv2d_3', 'conv2d_4', 'conv2d_5', 'conv2d_6']) #'conv2d_4',
