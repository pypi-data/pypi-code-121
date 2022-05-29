import subprocess
import shutil


subprocess.run(["python", "test_basic.py"])
subprocess.run(["python", "test_config.py"])
subprocess.run(["python", "test_console.py"])
subprocess.run(["python", "test_outputs.py"])

shutil.move("./test_basic_results.txt",
            "../test_results/test_basic_results.txt")
shutil.move("./test_config_results.txt",
            "../test_results/test_config_results.txt")
shutil.move("./test_console_results.txt",
            "../test_results/test_console_results.txt")
shutil.move("./test_output_results.txt",
            "../test_results/test_output_results.txt")
