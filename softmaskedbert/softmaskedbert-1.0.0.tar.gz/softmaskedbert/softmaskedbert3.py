import torch
from model import softMaskedBert, biGruDetector
from torch.utils.data import DataLoader
from torch import nn
from data import myData, collect_fn
from transformers import BertModel, BertTokenizer
from config import Config


class SmbModel(nn.Module):
    def __init__(self, config):
        super(SmbModel, self).__init__()
        self.config = config

        # bert的模块引用
        self.tokenizer = BertTokenizer.from_pretrained(self.config.vocab_file)
        self.bert = BertModel.from_pretrained(self.config.bert_path)
        self.vocab_size = self.tokenizer.vocab_size
        self.embedding = self.bert.embeddings
        self.masked_e = self.embedding(torch.tensor([[self.tokenizer.mask_token_id]], dtype=torch.long)).detach()
        self.detector_model = biGruDetector(self.config.embedding_size, self.config.hidden_size)
        self.corrector_model = softMaskedBert(
            self.config,
            vocab_size=self.vocab_size,
            masked_e=self.masked_e,
            bert_encoder=self.bert.encoder)

    def forward(self, input_, masks):
        input_ids = self.embedding(input_)
        detect_prob = self.detector_model(input_ids)
        correct_prob = self.corrector_model(input_ids,
                                            detect_prob,
                                            self.bert.get_extended_attention_mask(masks, input_ids.shape,
                                                                                  self.config.device))

        return detect_prob, correct_prob
    def inference(self, sentence):
        input_id = self.tokenizer.convert_tokens_to_ids(['[CLS]'] + list(sentence) + ['[SEP]'])
        masks = [1] * len(input_id)
        input_ = torch.tensor(input_id).view(1,-1)
        masks = torch.tensor(masks).float().view(1,-1)
        input_ids = self.embedding(input_)
        detect_prob = self.detector_model(input_ids)
        correct_prob = self.corrector_model(input_ids,
                                            detect_prob,
                                            self.bert.get_extended_attention_mask(masks, input_ids.shape,
                                                                                  self.config.device))
        detect_prob = detect_prob.flatten()
        detect_prob = detect_prob[1:-1]
        correct_prob = correct_prob[1:-1]
        return detect_prob,correct_prob

if __name__ == "__main__":
    config = Config()
    # 模型初始化
    model = SmbModel(config)
    # 数据构造
    train_dataset = myData(config, 'train')
    train_data_loader = DataLoader(dataset=train_dataset, batch_size=config.batch_size,
                                   collate_fn=collect_fn, shuffle=True)
    test_dataset = myData(config, 'dev')
    test_data_loader = DataLoader(dataset=test_dataset, batch_size=config.batch_size,
                                   collate_fn=collect_fn, shuffle=True)
    # 优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)
    # 损失函数计算
    detector_criterion = nn.BCELoss()
    corrector_criterion = nn.NLLLoss()
    # 训练
    step = 0
    
    for epoch in range(config.epoch):
        # 训练
        detect_TP = 0
        P = 0
        print('epoch:', epoch)
        model.train()
        for idx, batch_data in enumerate(train_data_loader):
#             print('epoch:', epoch, '******* step:', step)
            if hasattr(torch.cuda, 'empty_cache'):
                torch.cuda.empty_cache()
            step += 1
            batch_inp_ids, batch_out_ids, batch_labels, batch_mask, intexts, outtexts = batch_data
            batch_out_ids = batch_out_ids.to(config.device)  # 选择计算设备，下同
            batch_labels = batch_labels.to(config.device)
            batch_mask = batch_mask.to(config.device)
            batch_inp_ids = batch_inp_ids.to(config.device)
            detect_prob, correct_prob = model.forward(batch_inp_ids, batch_mask)
            detector_loss = detector_criterion(detect_prob.squeeze() * batch_mask, batch_labels.float())
            corrector_loss = corrector_criterion(
                (correct_prob * batch_mask.unsqueeze(-1)).reshape(-1, correct_prob.shape[-1]),
                batch_out_ids.reshape(-1))
            loss = config.gama * corrector_loss + (1 - config.gama) * detector_loss  # 联合loss
            optimizer.zero_grad()  # 每次迭代需梯度置零
            # 这里有个小技巧，梯度不置零可以近似获得增大batch_size的效果，以减少显存不足的限制，比如每两个batch，梯度归零一次
            # 因为tf默认执行这个操作，学习torch之后才发现的
            loss.backward(retain_graph=True)
            optimizer.step()
            for sentence_id in range(batch_inp_ids.shape[0]):
                pred = detect_prob[sentence_id].flatten().argmax()
                P += 1
                if batch_labels[sentence_id][pred]==1:
                    detect_TP += 1
            if step % 200 ==0:
                print('step:',step)
                print('detector_loss:',detector_loss)
                print('corrector_loss:',corrector_loss)
                print('train detect_TP:', detect_TP)
                print('train detect_P:', P)
         # 存模型
        torch.save(model, f'checkpoints/skpt_epoch{epoch}.pt')
        model.eval()
        detect_TP = 0
        correct_TP = 0
        P = 0
        with torch.no_grad():
            for idx, batch_data in enumerate(test_data_loader):
                batch_inp_ids, batch_out_ids, batch_labels, batch_mask, intexts, outtexts = batch_data
                batch_out_ids = batch_out_ids.to(config.device)  # 选择计算设备，下同
                batch_labels = batch_labels.to(config.device)
                batch_mask = batch_mask.to(config.device)
                batch_inp_ids = batch_inp_ids.to(config.device)
               
                detect_prob, correct_prob = model.forward(batch_inp_ids, batch_mask)

                for sentence_id in range(batch_inp_ids.shape[0]):
                    pred = detect_prob[sentence_id].flatten().argmax()
                    P += 1
                    if batch_labels[sentence_id][pred]==1:
                        detect_TP += 1
            print('eval detect_TP:', detect_TP)
            print('eval detect_P:', P)
            
            

