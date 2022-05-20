from bluesky import plan_stubs as bps
from ophyd import Component as Cpt
from ophyd import Device, EpicsSignal, EpicsSignalRO


class DensoOphydRobot(Device):
    """
    Represents the sample mounting Robot at NYX

    To mount a sample:
        1. Check that busy_sts is 0 and mount_ready_sts is 1
        2. Write the sample letter to puck_num_sel
        3. Write the sample number to sample_num_sel
        4. Check that sample_sts contains the desired sample
        5. Write 1 to mount_cmd (takes a while to return, use put_complete)
        6. Check that spindle_occupied_sts is 1 and busy_sts is 0

    Similar steps to dismount and check a sample.
    """

    # Status
    #
    # Status code is a bitfield.
    # Each subsequent *_sts signal is tied to a single
    # status bit

    # Status Code [int]
    status = Cpt(EpicsSignalRO, "Sts-Sts")

    # Is busy [bool]
    busy_sts = Cpt(EpicsSignalRO, "Busy-Sts")

    # Is ready to mount [bool]
    mount_ready_sts = Cpt(EpicsSignalRO, "MntRdy-Sts")

    # Is mounting [bool]
    mounting_sts = Cpt(EpicsSignalRO, "Mntng-Sts")

    # Is dismounting [bool]
    dismounting_sts = Cpt(EpicsSignalRO, "Dmntng-Sts")

    # Is drying [bool]
    drying_sts = Cpt(EpicsSignalRO, "Drying-Sts")

    # Spindle is occupied [bool]
    spindle_occupied_sts = Cpt(EpicsSignalRO, "Occ-Sts")

    # Error
    #
    # Error code is a bitfield.
    # Each subsequent *_err signal is tied to a single
    # error bit

    # Error code [int]
    error = Cpt(EpicsSignalRO, "Err-Sts")

    # Goniometer information not available [bool]
    gon_info_err = Cpt(EpicsSignalRO, "GonInfNA-Err")

    # Fluorescence detector is extended [bool]
    fl_det_ext_err = Cpt(EpicsSignalRO, "FlDetExt-Err")

    # Cryoststream not retracted [bool]
    cryo_not_ret_err = Cpt(EpicsSignalRO, "CryNotRet-Err")

    # No sample [bool]
    no_sample_err = Cpt(EpicsSignalRO, "NoSamp-Err")

    # Gripper stuck [bool]
    gripper_stuck_err = Cpt(EpicsSignalRO, "GrpStuck-Err")

    # Gripper sticky [bool]
    gripper_sticky_err = Cpt(EpicsSignalRO, "GrpStick-Err")

    # Spindle occupied [bool]
    spindle_occupied_err = Cpt(EpicsSignalRO, "SpiOcc-Err")

    # Dry cycle timeout [bool]
    dry_cycle_timeout_err = Cpt(EpicsSignalRO, "DryCycTmout-Err")

    # Unknown error [bool]
    unknown_err = Cpt(EpicsSignalRO, "Unknown-Err")

    # Sample selection
    #
    # Select a puck letter A-P
    # Select a sample number 1-16
    # The resulting sample will be held in sample_sts

    # Puck selection (enum, "A" - "P")
    puck_num_sel = Cpt(EpicsSignal, "PuckNum-Sel", put_complete=True)

    # Sample selection (enum, "1" - "16")
    sample_num_sel = Cpt(EpicsSignal, "SampleNum-Sel", put_complete=True)

    # Selected sample (string, example: "12B")
    # This is the sample that is going to be used by
    # the Mount, Dismount and Check commands
    sample_sts = Cpt(EpicsSignalRO, "Sample-Str")

    # Commands
    #
    # Write 1 to the signal to execute the command

    # Start drying (no arguments)
    dry_cmd = Cpt(EpicsSignal, "Dry-Cmd", put_complete=True)

    # Move to the center position (no arguments)
    center_cmd = Cpt(EpicsSignal, "Center-Cmd", put_complete=True)

    # Move to the safe position (no arguments)
    safe_cmd = Cpt(EpicsSignal, "Safe-Cmd", put_complete=True)

    # Clear "spindle occupied" state (no arguments)
    clear_cmd = Cpt(EpicsSignal, "Clear-Cmd", put_complete=True)

    # Mount sample - will mount sample specified in sample_sts
    mount_cmd = Cpt(EpicsSignal, "Mount-Cmd", put_complete=True)

    # Dismount sample - will dismount sample specified in sample_sts
    dismount_cmd = Cpt(EpicsSignal, "Dismount-Cmd", put_complete=True)

    # Check sample - will check sample specified in sample_sts
    check = Cpt(EpicsSignal, "Check-Cmd", put_complete=True)

    def set_sample(self, puck: str, sample: str):
        sample_str = f"{sample}{puck}"
        yield from bps.abs_set(self.puck_num_sel, puck, wait=True)
        yield from bps.abs_set(self.sample_num_sel, sample, wait=True)

        if self.sample_sts.get(use_monitor=False) != sample_str:
            raise RuntimeError(f"Failed to set sample '{sample_str}'")

        return sample_str

    def mount(self, puck: str, sample: str):
        if self.busy_sts.get() or not self.mount_ready_sts.get():
            raise RuntimeError("Can't mount: busy or occupied")

        sample_str = yield from self.set_sample(puck, sample)

        yield from bps.abs_set(self.mount_cmd, 1, wait=True)

        # Wait a little
        # TODO: remove
        yield from bps.sleep(0.5)

        if not self.spindle_occupied_sts.get(use_monitor=False):
            raise RuntimeError(f"Can't mount {sample_str}: failed to mount")

    def dismount(self, puck: str, sample: str):
        sample_str = f"{sample}{puck}"
        if self.busy_sts.get() or not self.spindle_occupied_sts.get():
            raise RuntimeError(f"Can't dismount {sample_str}: busy or empty")

        sample_str = yield from self.set_sample(puck, sample)

        yield from bps.abs_set(self.dismount_cmd, 1, wait=True)

        # Wait a little
        # TODO: remove
        yield from bps.sleep(0.5)

        if self.spindle_occupied_sts.get(use_monitor=False):
            raise RuntimeError(f"Can't dismount {sample_str}: failed to dismount")
