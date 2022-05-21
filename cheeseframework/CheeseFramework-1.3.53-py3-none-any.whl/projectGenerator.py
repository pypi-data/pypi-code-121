#cheese

import os
import git
import shutil
import stat

from Cheese.resourceManager import ResMan

"""
Generates structure of Cheese Application
"""

class ProjectGenerator:

    @staticmethod
    def generate(path, generateFiles):
        name = ResMan.getFileName(path)

        repo = git.Repo.clone_from("https://github.com/KubaBoi/CheeseFramework.git", path)

        repo.git.checkout("template")  

        for root, dirs, files in os.walk(os.path.join(path, ".git")):  
            for dir in dirs:
                os.chmod(os.path.join(root, dir), stat.S_IRWXU)
            for file in files:
                os.chmod(os.path.join(root, file), stat.S_IRWXU)
        shutil.rmtree(os.path.join(path, ".git"))

        src = os.path.join(path, "src")

        if (not generateFiles):
            os.remove(os.path.join(src, "controllers", "HelloWorldController.py"))
            os.remove(os.path.join(src, "models", "Hello.py"))
            os.remove(os.path.join(src, "repositories", "helloRepository.py"))

        with open(os.path.join(src, "mainTemplate.py"), "r") as f:
            data = f.read()

        with open(os.path.join(src, f"{name}.py"), "w") as f:
            f.write(data)

        os.remove(os.path.join(src, "mainTemplate.py"))