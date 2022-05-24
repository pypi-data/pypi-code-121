def byte_length_format(byte_length):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (byte_length / size) < 1:
            return "%.2f%s" % (byte_length, units[i])
        byte_length = byte_length / size


