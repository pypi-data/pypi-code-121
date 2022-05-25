from dsframework.testable.trainer_base import TrainerBase

class generatedClass(TrainerBase):
    @staticmethod
    def get_defaults():
        cfg = {}
        return cfg

    def __init__(self, name:str="generatedClassName",  **kwargs):
        TrainerBase.__init__(self, name, generatedClass.get_defaults(),  **kwargs)
        self.ready = False



# if __name__ == '__main__':
