from math import cos, sin, radians
from enum import Enum
from threading import Thread
from functools import partial
from time import sleep

class ActionType(Enum):
    ROTATE = 0
    MOVE   = 1
    SCALE  = 2
    WAIT   = 3

class Action:
    def __init__(self, action_type, value, duration=0, bone=None, sync=False):
        self.type = action_type
        self.value = value
        self.duration = duration
        self.bone = bone
        self.sync = sync
    
    def do(self, ctx, skeleton):
        if self.sync:
            thread = Thread(target=self._do, args=(ctx, skeleton))
            thread.start()
            return thread
        else:
            self._do(ctx, skeleton)
    def _do(self, ctx, skeleton):
        if self.type == ActionType.ROTATE:
            func = (skeleton if self.bone == None else skeleton.get_bone(self.bone)).rotate
            if self.duration > 0:
                for i in range(round(self.duration / 10)):
                    if not ctx.do:
                        break
                    func(self.value / self.duration * 10)
                    sleep(0.01)
            else:
                func(self.value)
        elif self.type == ActionType.MOVE:
            func = skeleton.move
            if self.duration > 0:
                for i in range(round(self.duration / 10)):
                    if not ctx.do:
                        break
                    func(self.value[0] / self.duration * 10 * skeleton.backbone.factor, self.value[1] / self.duration * 10 * skeleton.backbone.factor)
                    sleep(0.01)
            else:
                func(self.value)
        elif self.type == ActionType.SCALE:
            (skeleton if self.bone == None else skeleton.get_bone(self.bone)).scale(self.value)
        elif self.type == ActionType.WAIT:
            sleep(self.value / 1000)

class Animation:
    def __init__(self, *actions):
        self.actions = actions
    
    def add_action(self, action):
        self.actions.append(action)
    
    def play(self, skeleton):
        ctx = AnimationContext(skeleton)
        ctx.start(Thread(target=self._play, args=(skeleton, ctx)))
        return ctx
    def _play(self, skeleton, ctx, fd=True):
        threads = []
        for action in self.actions:
            if not ctx.do:
                break
            threads.append(action.do(ctx, skeleton))
        if fd:
            for thread in threads:
                if thread != None:
                    thread.join()
            ctx.do = False
    def loop(self, skeleton):
        ctx = AnimationContext(skeleton)
        ctx.start(Thread(target=self._loop, args=(skeleton, ctx)))
        return ctx
    def _loop(self, skeleton, ctx):
        while ctx.do:
            self._play(skeleton, ctx, False)
        ctx.do = False
    def stop(self, ctx):
        ctx.do = False
        ctx.skeleton.reset()
    def wait(self, ctx, fnc):
        Thread(target=self._wait, args=(ctx, fnc)).start()
    def _wait(self, ctx, fnc):
        while ctx.do: sleep(0.01)
        fnc()

class AnimationContext:
    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.do = False
    def start(self, thread):
        self.do = True
        self.thread = thread
        self.thread.start()

class Pose:
    def __init__(self, **bones):
        if type(bones.get("parent", None)) == Pose:
            self.bones = bones["parent"].bones.copy()
            del bones["parent"]
            self.bones.update(bones)
        else:
            self.bones = bones
        self__setitem__ = self.bones.__setitem__
        self__getitem__ = self.bones.__getitem__
    
    def apply(self, skeleton):
        skeleton.pose = self
        skeleton.pos = skeleton.backbone.pos
        for name, bone in skeleton.bones.items():
            if name in self.bones:
                bone.set_rotation(self.bones[name])
            elif type(bone) == Backbone:
                bone.set_rotation(90)

class Skeleton:
    def __init__(self, name):
        self.name = name
        self.pose = None
        self.pos = 0, 0
        self.bones = {}
    
    def add_bone(self, name, bone):
        self.bones[name] = bone
    def __setitem__(self, name, value):
        return self.add_bone(name, value)
    def get_bone(self, name):
        return self.bones[name]
    def __getitem__(self, name):
        return self.get_bone(name)
    def get_backbone(self):
        for bone in self.bones.values():
            if type(bone) == Backbone:
                return bone
    backbone = property(get_backbone)
    
    def move(self, x, y):
        self.backbone.move(x, y)
    def moveto(self, x, y):
        self.backbone.moveto(x, y)
    
    def reset(self):
        self.backbone.moveto(*self.pos)
        if self.pose != None:
            self.pose.apply(self)
    
    def mirror(self):
        for bone in self.bones.values():
            bone.mirror()
    
    def rotate(self, degrees):
        self.backbone.rotate(degrees)
    
    def scale(self, factor):
        for bone in self.bones.values():
            bone.scale(factor)

class Bone:
    def __init__(self, parent, offset, length, angle):
        self.parent = parent
        self.offset = offset
        self.factor = 0
        self.length = self.original_length = length
        self.mirrored = False
        self.angle = angle
        self.normalize_angle()
    
    def scale(self, factor):
        self.factor = factor
        self.length = self.original_length * self.factor
    
    def mirror(self):
        self.mirrored = not self.mirrored
    
    def set_rotation(self, degrees):
        self.angle = degrees
        self.normalize_angle()
    
    def get_rotation(self):
        angle = (180 if type(self.parent) == Backbone else 0) - self.angle + (180 if type(self.parent) != Backbone and type(self.parent.parent) == Backbone else 0) - self.parent.angle if self.mirrored else self.angle + self.parent.angle
        if angle >= 360:
            angle %= 360
        elif angle < 0:
            angle = 360 + angle
        return angle
    
    def rotate(self, degrees):
        self.angle += -degrees if self.mirrored and type(self) == Backbone else degrees
        self.normalize_angle()
    
    def normalize_angle(self):
        if self.angle >= 360:
            self.angle %= 360
        elif self.angle < 0:
            self.angle = 360 + (self.angle % -360)
        else:
            return
        self.normalize_angle()
    
    def get_center(self):
        points = self.get_points()
        return ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
    
    def get_points(self):
        first = self.parent.get_points()[1]
        angle = self.parent.get_rotation()
        off = - (self.offset * self.parent.length / 100)
        offset = off * cos(radians(angle)), off * sin(radians(angle))
        first = first[0] + offset[0], first[1] + offset[1]
        angle = self.get_rotation()
        second = (first[0] + (self.length * cos(radians(angle))), first[1] + (self.length * sin(radians(angle))))
        return (first, second)

class Backbone(Bone):
    def __init__(self, x, y, length, angle):
        self.pos = x, y
        self.factor = 0
        self.length = self.original_length = length
        self.mirrored = False
        self.angle = angle
        self.normalize_angle()
    
    def move(self, x, y):
        self.pos = self.pos[0] + x, self.pos[1] + y
    def moveto(self, x, y):
        self.pos = x, y
    
    def get_rotation(self):
        return self.angle
    
    def get_points(self):
        return (self.pos, (self.pos[0] + (self.length * cos(radians(self.angle))), self.pos[1] + (self.length * sin(radians(self.angle)))))


