import torch.nn as nn
import torch.nn.functional as F

class cnn_block(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv1d(20, 32, kernel_size=3, stride=1)
        self.norm1 = nn.BatchNorm1d(64)

        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, stride=1)
        self.norm1 = nn.BatchNorm1d(64)

        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, stride=1)
        self.norm1 = nn.BatchNorm1d(64)

        self.conv4 = nn.Conv1d(128, 256, kernel_size=3, stride=1)
        self.norm1 = nn.BatchNorm1d(64)

        self.conv5 = nn.Conv1d(256, 512, kernel_size=3, stride=1)
        self.norm1 = nn.BatchNorm1d(64)
        self.norm1 = nn.BatchNorm1d(32)
        self.norm2 = nn.BatchNorm1d(64)
        self.maxpool = nn.AvgPool1d(4, 4)   
        self.avgpool = nn.AvgPool1d(4, 4)   

    def forward(self,x):
        x = F.relu(self.conv1(x))
        # x = self.norm1(x)
        x = self.avgpool(x)

        x = F.relu(self.conv2(x))
        # x = self.norm2(x)
        x = self.avgpool(x)

        x = F.relu(self.conv3(x))
        x = self.maxpool(x)

        x = F.relu(self.conv4(x))
        x = self.maxpool(x)

        x = F.relu(self.conv5(x))
        x = self.maxpool(x)
        return x

class siamese_cnn(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.cnn_block = cnn_block()
        self.fc1 = nn.Linear(1024,128)
        self.fc2 = nn.Linear(128,2)
        self.flatten = nn.Flatten()
        self.softmax = nn.Softmax()
        # self.dropout = nn.Dropout(0.5)


    def forward(self,x1,x2):
        x1 = self.cnn_block(x1)
        x1 = self.flatten(x1)
        x2 = self.cnn_block(x2)
        x2 = self.flatten(x2)
        x = torch.cat((x1,x2),1)
        x = F.relu(self.fc1(x))
        # x = self.dropout(x)
        x = self.fc2(x)
        return x

class cnn(nn.Module):
    def __init__(self):
        super(siamese, self).__init__()
        self.conv1 = nn.Conv1d(20, 32, 3)
        self.norm1 = nn.BatchNorm1d(32)
        self.pool1 = nn.AvgPool1d(4, 4)

        self.conv2 = nn.Conv1d(32, 64, 3)
        self.norm2 = nn.BatchNorm1d(64)
        self.pool2 = nn.AvgPool1d(4, 4)

        self.conv3 = nn.Conv1d(64, 128, 3)
        self.norm3 = nn.BatchNorm1d(128)
        self.pool3 = nn.AvgPool1d(4, 4)

        self.conv4 = nn.Conv1d(128, 256, 3)
        self.norm4 = nn.BatchNorm1d(256)
        self.pool4 = nn.MaxPool1d(4, 4)

        self.conv5 = nn.Conv1d(256, 512, 3)
        self.norm5 = nn.BatchNorm1d(512)
        self.pool5 = nn.MaxPool1d(4, 4)

        self.fc1 = nn.Linear(3584, 64)
        self.fc2 = nn.Linear(64, 2)
        self.dropout = nn.Dropout(0.2)
        # self.sig = nn.Softmax()

    def forward(self, x):
        batch_size = x.shape[0]
        x = self.pool1(F.relu(self.norm1(self.conv1(x))))
        x = self.pool2(F.relu(self.norm2(self.conv2(x))))
        x = self.pool3(F.relu(self.conv3(x)))
        x = self.pool4(F.relu(self.conv4(x)))
        x = x.view(batch_size,-1)

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.softmax(self.fc2(x), dim = 1)

        return x

