# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

from argparse import ArgumentParser
from time import sleep

from phootonics_controller.base_controllers.stage_vcm import VCMirrorController

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', type=str, required=True)
    parser.add_argument('-a', type=float, required=True)
    args = parser.parse_args()
    vcmc = VCMirrorController(args.mirror)
    vcmc.start()
    while True:
        if vcmc.status == "READY":
            break
        sleep(0.2)
    vcmc.move_to_angle(args.a)
    print(vcmc.get_angle())
    vcmc.stop()

