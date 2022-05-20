from conans import ConanFile, CMake
# import os

class KnuthPyNative(ConanFile):
    name = "knuth-py-native"
    version = "0.1"
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/k-nuth/py-native"
    description = "Bitcoin Full Node Library with Python interface"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    requires = (("c-api/0.25.0@kth/stable"))

    def configure(self):
        ConanFile.configure(self)
        self.options["c-api"].db = "full"
        self.options["c-api"].march_id = "4fZKi37a595hP"
        self.options["c-api"].shared = False

    def imports(self):
        # self.copy("*.h", "./kth/include/kth", "include/kth")
        # self.copy("*.hpp", dst="./kth/include/kth", src="include/kth")
        # self.copy("*.dylib", dst="./kth/lib", src="lib")
        # self.copy("*.so", dst="./kth/lib", src="lib")
        # self.copy("*.lib", dst="./kth/lib", src="lib")
        # self.copy("*.dll", dst="./kth/lib", src="lib")
        self.copy("*.h", "./kth/include/kth", "include/kth")
        self.copy("*.hpp", dst="./kth/include/kth", src="include/kth")

        self.copy("*.lib", dst="./kth/lib", src="lib")
        self.copy("*.a", dst="./kth/lib", src="lib")
        self.copy("*.dylib", dst="./kth/lib", src="lib")
        self.copy("*.so", dst="./kth/lib", src="lib")
        self.copy("*.dll", dst="./kth/lib", src="lib")

        # self.copy("*.h", dst="/Users/fernando/fertest", src="include/kth")
        # self.copy("*.hpp", dst="/Users/fernando/fertest", src="include/kth")
        # self.copy("*.dylib", dst="/Users/fernando/fertest", src="lib")

    # def build(self):
    # def package(self):
    # def package_info(self):
