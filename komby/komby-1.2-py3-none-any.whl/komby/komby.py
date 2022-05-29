import math


class Komby:

    @staticmethod
    def total_partitions(data):
        """
        Compute the total of possible partitions of a list.

        :param data: the list
        :return: int
        """
        n = len(data)

        if n == 0:
            return 0

        return int(math.pow(2, (n - 1)))

    @staticmethod
    def partitions(data, sorted=False, size=0):
        """
        Create the partitions of a list.

        For a list with the values [1, 2, 3], 4 partitions will be created:

        Partition 0: [[1,2,3]] with only one element with all the values in the list
        Partition 1: [[1,2],[3]]
        Partition 2: [[1],[2,3]]
        Partition 3: [[1],[2],[3]] with each element in the list in a partition.

        :param data: the list
        :param sorted: return the partitions sorted by the size of the partition
        :param size: get only the partitions with a specific size, if size == 0 all the partitions will be created
        :return: []
        """

        if not type(data) == list:
            raise TypeError("The data must be a list.")

        if size < 0:
            print(size)
            raise TypeError("the size must be greater than -1.")

        partitions = []
        total = Komby.total_partitions(data)
        n = len(data) - 1

        if total == 0:
            return []

        for i in range(total):
            aux = []
            aux2 = []
            aux_str = "".join(bin(i))[2:].zfill(n)
            aux2.append(data[0])
            for j in range(n):
                # create a new partition
                if aux_str[j] == "1":
                    aux.append(aux2)
                    aux2 = []

                # add the next value to the segment
                aux2.append(data[j + 1])
            aux.append(aux2)
            partitions.append(aux)

        if sorted:
            partitions.sort(key=len)

        if size > 0:
            prt = []
            for p in partitions:
                if len(p) == size:
                    prt.append(p)

            return prt
        else:
            return partitions
