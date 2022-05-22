#!/usr/bin/env python3

import time
from typing import Callable, Any

from pygame import Surface


class ParticleManager:
    """
    ParticleManager

    Type: class

    Description: this class keeps track, updates and removes dynamically
        particles given some functions

    Args:
        'draw_func' (function): a function that takes two arguments,
            the particle and the surface and draws it onto the given
            surface
        'update_func' (function): a function that takes one argument,
            the particle and updates it
        'deletion_check' (function): a function that takes one argument,
            the particle and returns True if the particle is to be
            deleted, an example is at the end of a timer or with an
            alpha of 0
        'update_rate' (float): time interval between updates, unlike
            animations, if the frame rate is below the update_rate, this
            slows down

    Args:
        'particles' (list): the list of the particles
        'draw_func' (function): see 'draw_func' in args
        'update_func' (function): see 'update_func' in args
        'deletion_check' (function): see 'deletion_check' in args
        'update_rate' (float): see 'update_rate' in args
        'last_updated' (float): last time it was updates, uses
            time.perf_counter

    Methods:
        - add_particle(particle: Any)
        - update()
        - draw(surface)
    """
    def __init__(self,
                 draw_func: Callable,
                 update_func: Callable,
                 deletion_check: Callable,
                 update_rate: float = 0):
        self.particles = []
        self.draw_func = draw_func
        self.update_func = update_func
        self.del_check = deletion_check
        self.update_rate = update_rate
        self.last_updated = time.perf_counter()

    def add_particle(self, particle: Any) -> None:
        """
        add_particle(self, particle)

        Type: method

        Description: adds a particle to 'particles'

        Args:
            'particle' (Any): the particle to add

        Return type: None
        """
        self.particles.append(particle)

    def update(self) -> None:
        """
        update(self)

        Type: method

        Description: updates all the particles

        Return type: None
        """
        to_del = []
        for idx, particle in enumerate(self.particles):
            self.update_func(particle)
            if self.del_check(particle):
                to_del.append(idx)
        for i in reversed(to_del):
            del self.particles[i]

    def draw(self, surface: Surface) -> None:
        """
        draw(self, surface)

        Type: method

        Description: updates all the particles

        Args:
            'surface' (pygame.Surface): the surface to pass to 'draw_func'

        Return type: None
        """
        if time.perf_counter() - self.last_updated > self.update_rate:
            self.update()
            self.last_updated = time.perf_counter()
        for i in self.particles:
            self.draw_func(i, surface)
