from transformers import AutoConfig

class PrefixPromptConfig(AutoConfig):
    def __init__(self):
        super().__init__()
        self.prefix_hidden_size = None
        self.pre_seq_len = None
        self.prefix_projection = None

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path,pre_seq_len=8,prefix_hidden_size=512,prefix_projection=True, **kwargs):
        config_obj = AutoConfig.from_pretrained(pretrained_model_name_or_path)
        config_obj.pre_seq_len = pre_seq_len
        config_obj.prefix_hidden_size = prefix_hidden_size
        config_obj.prefix_projection = prefix_projection
        return config_obj



if __name__ == '__main__':
    model_name = "roberta-large"

    config = PrefixPromptConfig.from_pretrained(model_name)
    print(config)