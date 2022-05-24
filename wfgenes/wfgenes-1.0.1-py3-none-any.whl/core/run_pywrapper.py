import node_1001_1105_parsl
#import node_501_592_parsl


if __name__ == '__main__':
    
    core_number = [80, 70 , 60, 50, 40, 30, 20, 10, 8, 4, 2, 1]
    
    for core in core_number:
        node_1001_1105_parsl.run_model(core)
    