import os
from run_kotlin_kernel.run_kernel import module_install_path


def detect_jars_location():
    run_kernel_path = module_install_path()
    jars_dir = os.path.join(run_kernel_path, 'jars')
    print(str(jars_dir))


if __name__ == '__main__':
    detect_jars_location()
