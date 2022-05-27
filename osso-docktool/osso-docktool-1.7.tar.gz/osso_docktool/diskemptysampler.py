from base64 import b16encode
from hashlib import md5
import random
import time

__author__ = 'osso'


def hexdigest(data):
    return b16encode(data).decode('ascii').lower()


class SpuriousReadError(OSError):
    pass


class DiskEmptySampler(object):
    """
    Divide the disk in 'sample_count' regions
    and sample (md5sum) 'sample_size' bytes randomly per region
    """
    def __init__(self, devname, sample_count=100, sample_size=(1024 * 1024)):
        self.devname = devname

        # No divide by zero errors
        if sample_count == 0:
            raise Exception('Sample size should not be zero')

        self.sample_count = sample_count
        self.sample_size = sample_size

        self.sample_regions = None
        self.sample_runs = []

        self.expected_hash = hexdigest(md5(b'\x00' * sample_size).digest())

    def sample(self):
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                samples = self._sample_disk()
            except SpuriousReadError:
                if attempt == attempts:
                    raise
                print('WARNING: Read error. Possibly too fast after disk wipe')
                time.sleep(5)
                print('Retrying...')
            else:
                self.sample_runs.append(samples)
                break

    def is_zero(self):
        assert self.sample_runs, repr(self.sample_runs)
        samples = self.sample_runs[-1]
        assert samples, repr(samples)

        for sample_nr, md5_sum in enumerate(samples):
            if hexdigest(md5_sum) != self.expected_hash:
                print('Digests are unexpected: {} != {}'.format(
                    hexdigest(md5_sum), self.expected_hash))
                print('for offset: {} (sample_size: {})'.format(
                    self.sample_regions[sample_nr], self.sample_size))
                return False

        return True

    def is_different(self):
        assert self.sample_runs and len(self.sample_runs) >= 2, repr(
            self.samples)
        samples_1 = self.sample_runs[-2]
        samples_2 = self.sample_runs[-1]

        both_samples = zip(samples_1, samples_2)
        for sample_nr, (md5_1, md5_2) in enumerate(both_samples):
            if md5_1 == md5_2:
                print('Digests are equal between runs: {}'.format(
                    hexdigest(md5_1)))
                print('for offset: {} (sample_size: {})'.format(
                    self.sample_regions[sample_nr], self.sample_size))
                return False
        return True

    def _sample_disk(self):
        with open(self.devname, 'rb') as fp:
            if not self.sample_regions:
                self.sample_regions = self._generate_sample_regions(
                    fp, self.sample_count, self.sample_size)

            samples = []

            # Loop over the sample_regions (offsets) and store the md5 of that
            # region.
            assert self.sample_regions
            for sample_nr, offset in enumerate(self.sample_regions):
                # Jump there, and fetch block.
                fp.seek(offset)
                try:
                    data = fp.read(self.sample_size)
                except OSError as e:
                    # On NVMe drives, we have seen that a read() here
                    # fails immediately after an nvme sanitize
                    # operation. The SpuriousReadError allows us to back
                    # off and retry after a little sleep.
                    errno = e.args[0]
                    if errno == 5:  # EIO
                        raise SpuriousReadError() from e
                    raise

                # Create md5 and store for later inspection.
                samples.append(md5(data).digest())

        return samples

    @staticmethod
    def _generate_sample_regions(fp, sample_count, sample_size):
        regions = []

        # Get the size of disk (e.g. 256GB).
        size = fp.seek(0, 2)

        # Divide the disk into sample_regions (e.g. 256GB/2000 = ~131MB).
        sample_region_size = size // sample_count

        # Check if the regions are large enough to get a sample from.
        if sample_size > sample_region_size:
            raise ValueError('Sample size is too large: {} > {}/{}'.format(
                sample_size, size, sample_count))

        # Loop over the sample_regions and select a random sample inside
        # that region:
        # - 0: first 131MB: choose a random sample_size block there
        # - 1: second 131MB: choose a random sample_size block there
        # ..etc..
        for sample_nr in range(sample_count):
            # Calculate begin and end of region based on sample_region
            # size and pick a random offset in it:
            region_start = sample_nr * sample_region_size
            region_end_ex = min((sample_nr + 1) * sample_region_size, size)
            offset = random.randint(
                region_start, region_end_ex - sample_size)
            regions.append(offset)

        return regions
