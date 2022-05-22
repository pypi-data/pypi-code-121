import warnings
import torch

warnings.filterwarnings('ignore')

class NeuralWatermark:
    def __init__(self, model=None, mark_type="C", device="cpu", trigger_loader=None) -> None:
        self.model = model
        self.mark_type = mark_type
        self.device = device
        self.trigger_loader = trigger_loader
    def get_watermark_keys(self):
        if self.mark_type == "C":
            assert self.trigger_loader != None, "For custom watermarking type, trigger dataset loader cannot be empty"
            return self.get_custom_keys()
        
    def get_custom_keys(self):
        X, Y = [], []
        for _, data in enumerate(self.trigger_loader):
            inputs, labels = data
            X += list(inputs.cpu().detach().numpy())
            Y += list(labels.cpu().detach().numpy())
            
        custom_keys = {}
        custom_keys['inputs'] = X
        custom_keys['labels'] = Y
        custom_keys['bounds'] = (min(Y), max(Y))

        return custom_keys

    def get_watermark_loss(self, criterion=None):
        assert criterion != None, "For custom watermarking type, trigger dataset loader cannot be empty"
        wmloss = 0
        if self.mark_type == "C":
            wmloss = self.calculate_watermark_loss_C(criterion)
        return wmloss

    def calculate_watermark_loss_C(self,criterion ):  
        markedloss = None
        for _, data in enumerate(self.trigger_loader):
            inputs, labels = data
            outputs = self.model(inputs.to(self.device))
            if not markedloss:
                markedloss = criterion(outputs, labels.to(self.device))
            else:
                markedloss += criterion(outputs, labels.to(self.device))
        return markedloss    