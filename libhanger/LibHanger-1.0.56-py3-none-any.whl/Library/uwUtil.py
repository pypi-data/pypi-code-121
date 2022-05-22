import psutil

def getDiskUsage():
    
    """
    ディスク使用量(%)
    """
    
    disk = psutil.disk_usage('/')
    
    return disk.percent

# ディスク使用量(%)
dskUsage = getDiskUsage()

# ディスク空き容量(%)
dskFree = 100 - dskUsage