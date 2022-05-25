import numpy as np


def cal_sdr(reference, estimation, sr=16000):
    """
    Scale-Invariant Signal-to-Distortion Ratio (SI-SDR)

    Args:
        reference: numpy.ndarray, [..., T]
        estimation: numpy.ndarray, [..., T]

    Returns:
        SI-SDR

    References
        SDR– Half- Baked or Well Done? (http://www.merl.com/publications/docs/TR2019-013.pdf)
    """
    estimation, reference = np.broadcast_arrays(estimation, reference)
    reference_energy = np.sum(reference ** 2, axis=-1, keepdims=True)

    optimal_scaling = np.sum(reference * estimation, axis=-1, keepdims=True) / reference_energy

    projection = optimal_scaling * reference

    noise = estimation - projection

    ratio = np.sum(projection ** 2, axis=-1) / np.sum(noise ** 2, axis=-1)
    return 10 * np.log10(ratio)


if __name__ == '__main__':
    with open('clean.pcm','rb') as ref:
        pcmdata = ref.read()
    with open('in.pcm','rb') as ref:
        indata = ref.read()
    ref = np.frombuffer(pcmdata,dtype=np.int16)
    ins = np.frombuffer(indata, dtype=np.int16)
    print(cal_sdr(ref,ins))