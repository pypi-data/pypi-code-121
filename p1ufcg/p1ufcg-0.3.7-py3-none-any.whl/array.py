class Array:
    def __init__(self, arg1, zero=None):
        if type(arg1) is list:
            self.size = len(arg1)
            self.data = arg1[:]

        elif type(arg1) is int:
            self.size = arg1
            self.data = self.size * [zero]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self)

    def check_index(self, index):
        assert 0 <= index < len(self.data), "array index out of range"

    def __setitem__(self, index, value):
        self.check_index(index)
        self.data[index] = value

    def __getitem__(self, index):
        self.check_index(index)
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __eq__(self, outro):
        if type(outro) is list:
            return self.data == outro
        return outro.data == self.data
