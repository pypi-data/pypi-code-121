# coding=utf-8

from flutter_gen.generate.generate_color_cmd import GenerateColorCommand
from flutter_gen.generate.generate_font_cmd import GenerateFontCommand
from flutter_gen.generate.generate_repo_cmd import GenerateRepoCommand
from flutter_gen.generate.generate_router_cmd import GenerateRouterCommand
from flutter_gen.generate.generate_image_cmd import GenerateImageCommand
from flutter_gen.generate.generate_localization_cmd import GenerateLocalizationCommand
from flutter_gen.generate.generate_object_mapper_cmd import GenerateObjectMapperCommand
from flutter_gen.utils.debounce import debounce
from flutter_gen.utils.print import print_info
from ..core.command import Command
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import multiprocessing
import time
import os


class WatchCommand(Command):
    def __init__(self):
        super(WatchCommand, self).__init__()

    def monitor(self, path, event, patterns=['*.dart']):
        patterns = patterns
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive)

        my_event_handler.on_created = event
        my_event_handler.on_deleted = event
        my_event_handler.on_modified = event
        my_event_handler.on_moved = event

        observer = Observer()
        observer.schedule(my_event_handler, path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def createFile(self, path):
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            print_info("Creating %s completed" % (path))
            with open(path, 'w'):
                pass

    # Gen Image
    def gen_image(self, event):
        self._gen_image(event)

    @debounce(1)
    def _gen_image(self, event):
        GenerateImageCommand().run()

     # Gen Localization
    def gen_localization(self, event):
        self._gen_localization(event)

    @debounce(1)
    def _gen_localization(self, event):
        GenerateLocalizationCommand().run()

    # Gen Object Mapper
    def gen_mapper(self, event):
        self._gen_mapper(event)

    @debounce(1)
    def _gen_mapper(self, event):
        GenerateObjectMapperCommand().run()

    # Gen Font
    def gen_font(self, event):
        self._gen_font(event)

    @debounce(1)
    def _gen_font(self, event):
        GenerateFontCommand().run()

    # Gen Color
    def gen_color(self, event):
        self._gen_color(event)

    @debounce(1)
    def _gen_color(self, event):
        GenerateColorCommand().run()

    # Gen Router
    def gen_router(self, event):
        self._gen_router(event)

    @debounce(1)
    def _gen_router(self, event):
        GenerateRouterCommand().run()

    # Gen Repositories
    def gen_repo(self, event):
        self._gen_repo(event)

    @debounce(1)
    def _gen_repo(self, event):
        GenerateRepoCommand().run()

    def build_runner(self):
        os.system('flutter pub run build_runner watch --delete-conflicting-outputs')

    def run(self):
        # Upgrade tools
        # os.system('pip3 install -U flutter_gen')
        # Gen file
        self.createFile("assets/color/colors.txt")
        # Gen all
        GenerateImageCommand().run()
        GenerateObjectMapperCommand().run()
        GenerateRouterCommand().run()
        GenerateColorCommand().run()
        GenerateLocalizationCommand().run()
        GenerateFontCommand().run()
        GenerateRepoCommand().run()
        # Start watch
        thread_mobx = multiprocessing.Process(
            target=self.build_runner)
        thread_mobx.start()
        thread_image = multiprocessing.Process(
            target=self.monitor, args=('./assets/images', self.gen_image, ['*.jpg', '*.png', '*.svg']))
        thread_image.start()
        thread_mapper = multiprocessing.Process(
            target=self.monitor, args=('./lib/models', self.gen_mapper))
        thread_mapper.start()
        thread_mapper_api = multiprocessing.Process(
            target=self.monitor, args=('./lib/data/api', self.gen_mapper))
        thread_mapper_api.start()
        thread_color = multiprocessing.Process(
            target=self.monitor, args=('./assets/color', self.gen_color, ['colors.txt']))
        thread_color.start()
        thread_router = multiprocessing.Process(
            target=self.monitor, args=('./lib/scenes', self.gen_router, ['app_pages.dart', '*_viewmodel.dart']))
        thread_router.start()
        thread_repo = multiprocessing.Process(
            target=self.monitor, args=('./lib/data/repositories', self.gen_repo, ['*_repository.dart']))
        thread_repo.start()
        thread_localization = multiprocessing.Process(
            target=self.monitor, args=('./assets/i18n', self.gen_localization, ['*.json']))
        thread_localization.start()
        thread_font = multiprocessing.Process(
            target=self.monitor, args=('./', self.gen_font, ['pubspec.yaml']))
        thread_font.start()
