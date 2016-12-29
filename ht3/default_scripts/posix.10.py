"""Some good Posix Commands."""

from Env import *

if CHECK.os.posix:

    def complete_mount_device(s):
        for p in ('/dev/', '/dev/disk/by-label', '/dev/disk/by-partlabel'):
            p = Path(p)
            for dev in p.glob('*'):
                if dev.is_block_device():
                    yield dev.name

    @cmd
    def mount(device:complete_mount_device):
        """Mount a dvice by its label, partlabel or name.

        Creates a folder in /media for the name/label and mounts to it."""
        import os
        for d in ('/dev/', '/dev/disk/by-label', '/dev/disk/by-partlabel'):
            dev = Path(d) / device
            if dev.is_block_device():
                break
        else:
            raise ValueError("no such blockdevice", device)


        target = Path('/media') / device
        if target.exists():
            if not target.is_dir():
                raise ValueError("Not a directory", target)
        else:
            target.mkdir(parents=True)

        fstype = procio("lsblk", "-ln", "-oFSTYPE", str(dev)).strip()
        options = "nosuid,nodev,noexec,nosuid,relatime,fmask=113,dmask=002"
        if fstype == 'ext4':
            pass
        elif fstype in[
            'fat', 'vfat', 'umsdos', 'msdos','ntfs',
            'hfs', 'hpfs',
            'iso9660', 'udf']:
            options += ",uid={:d},gid={:d}".format(os.geteuid(), os.getegid())

        procio("sudo", "mount", "-t", fstype, str(dev), str(target), "--options", options)

    def complete_mounted_devices(s):
        with open('/proc/mounts') as f:
            for s in f:
                dev, mp, *_ = s.split()
                if Path(dev).is_block_device():
                    yield dev
                    yield mp
                    if mp.startswith('/media/'):
                        yield mp[7:]

    @cmd
    def umount(device:complete_mounted_devices):
        m = False
        device = Path(device)
        if not device.is_absolute():
            device = Path('/media/') / device
            m = True

        if not device.is_block_device() and not device.is_dir():
            raise ValueError("not blockdevice or mountpoint", device)

        procio('sudo', 'umount', str(device))

        if m:
            device.rmdir()


    @cmd(name='o')
    def xdg_open(s:Path):
        """Open something with xdg-open."""
        return execute_disconnected('xdg-open', s)
