"""Some good Posix Commands."""

if CHECK.os.posix:

    def _complete_mount_device(s):
        for p in ('/dev/', '/dev/disk/by-label', '/dev/disk/by-partlabel'):
            p = Path(p)
            for dev in p.glob('*'):
                if dev.is_block_device():
                    yield dev.name

    @cmd
    def mount(device:"mount_device"):
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

        fstyp = procio("lsblk", "-ln", "-o FILESYSTEM", str(dev))
        options = "nosuid,nodev,noexec,nosuid,relatime,fmask=113,dmask=002"
        if fstyp == 'ext4':
            pass
        elif fstype in[
            'fat', 'vfat', 'umsdos', 'msdos','ntfs',
            'hfs', 'hpfs',
            'iso9660', 'udf']:
            options += ",uid={:d},gid={:d}".format(os.geteuid(), os.getegid())

        procio("sudo", "mount", "-t", fstype, "-o", options)

    @cmd(name='o')
    def xdg_open(s):
        return execute_disconnected('xdg-open', s)
