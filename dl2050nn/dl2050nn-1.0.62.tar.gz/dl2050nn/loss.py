import torch


def NLLLoss(y2, y):
    out = torch.zeros_like(y, dtype=torch.float)
    for i in range(len(y)):
        out[i] = y2[i][y[i]]
    return -out.sum()/len(out)


# learner.logger.loss_t
# learner.logger.n
# learner.logger.x.shape[0]
# learner.logger.loss_t/learner.logger.n


# y = learner.y.detach().cpu()
# y2 = learner.y2.detach().cpu()

# loss = NLLLoss()(y2, y)
# loss