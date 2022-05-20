resblock = "1"
num_gpus = 0
batch_size = 16
learning_rate = 0.0002
adam_b1 = 0.8
adam_b2 = 0.99
lr_decay = 0.999
seed = 1234

upsample_rates = [5, 5, 4, 2]
upsample_kernel_sizes = [10, 10, 8, 4]
upsample_initial_channel = 512
resblock_kernel_sizes = [3, 7, 11]
resblock_dilation_sizes = [[1, 3, 5], [1, 3, 5], [1, 3, 5]]

segment_size = 6400
num_mels = 80
num_freq = 1025
n_fft = 1024
hop_size = 200
win_size = 800

sampling_rate = 16000

fmin = 0
fmax = 7600
fmax_for_loss = None

num_workers = 4
