

# class Normalize1():
#     def __init__(self, m, s, shift=[0,0,0]):
#         self.m, self.s, self.shift = torch.tensor(m), torch.tensor(s), torch.tensor(shift)
#     def __call__(self, x):
#         print(x.size())
#         print(self.m.size(), self.s.size(), self.shift.size())
#         return (x-self.m)/self.s - self.shift