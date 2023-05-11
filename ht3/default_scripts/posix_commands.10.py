"""Some good Posix Commands."""

import json

from Env import *

if CHECK.os.posix:

    @Env
    @cmd
    def sudo(*args, **kwargs):
        sudo = "sudo"
        if not CHECK.is_cli_frontend:
            try:
                execute(
                    "sudo -- true",
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                )  # check if we have a sudo cookie, or trigger non-password auth mechanisms
            except ProcIOException:
                sudo = "gksudo"
        return procio(sudo, *args, **kwargs)

    def complete_mount_device(s):
        def walk(d):
            if d["fstype"]:
                yield d["name"]
                if d["partlabel"]:
                    yield d["partlabel"]
                if d["label"]:
                    yield d["label"]
            if "children" in d:
                for c in d["children"]:
                    yield from walk(c)

        s = procio("lsblk", "--json", "--output", "name,label,partlabel,fstype")
        d = json.loads(s)
        for c in d["blockdevices"]:
            yield from walk(c)

    @cmd
    def mount(device: complete_mount_device):
        """Mount a dvice by its label, partlabel or name.

        Creates a folder in /media for the name/label and mounts to it."""
        import os

        for d in ("/dev/", "/dev/disk/by-label", "/dev/disk/by-partlabel"):
            dev = Path(d) / device
            if dev.is_block_device():
                break
        else:
            raise ValueError("no such blockdevice", device)

        target = Path("/media") / device
        if target.exists():
            if not target.is_dir():
                raise ValueError("Not a directory", target)
        else:
            target.mkdir(parents=True)

        fstype = procio("lsblk", "-ln", "-oFSTYPE", str(dev)).strip()
        if fstype == "ext4":
            options = "rw,nosuid,nodev,relatime"
        elif fstype in ["fat", "vfat", "umsdos", "msdos", "ntfs", "hfs", "hpfs", "udf"]:
            options = (
                "rw,nosuid,nodev,relatime,uid={:d},gid={:d},fmask=113,dmask=002".format(
                    os.geteuid(), os.getegid()
                )
            )
        elif fstype == "iso9660":
            options = (
                "nosuid,nodev,relatime,uid={:d},gid={:d},fmask=113,dmask=002".format(
                    os.geteuid(), os.getegid()
                )
            )

        show(f"mount -t {fstype} {dev} {target} --options {options}")
        return sudo(
            "mount",
            "-t",
            fstype,
            str(dev),
            str(target),
            "--options",
            options,
        )

    def complete_mounted_devices(s):
        with open("/proc/mounts") as f:
            for s in f:
                dev, mp, *_ = s.split()
                if Path(dev).is_block_device():
                    yield dev
                    yield mp
                    if mp.startswith("/media/"):
                        yield mp[7:]

    @cmd
    def umount(device: complete_mounted_devices):
        m = False
        device = Path(device)
        if not device.is_absolute():
            device = Path("/media/") / device
            m = True

        if not device.is_block_device() and not device.is_dir():
            raise ValueError("not blockdevice or mountpoint", device)

        sudo("umount", str(device))

        if m:
            device.rmdir()

    @cmd
    def bd():
        show(
            procio(
                "lsblk",
                "--output",
                "name,mountpoint,ro,fstype,size,label,partlabel,model",
            )
        )

    @Env
    @cmd(name="o")
    def xdg_open(s: Path):
        """Open something with xdg-open."""
        execute_disconnected("xdg-open", s)

    print("\x1b]2;HansTool\x07", end="")  # Set Title of Terminal Window

    @Env
    def get_clipboard():
        return procio("xclip", "-out", "-selection", "clipboard")

    @Env
    def set_clipboard(s):
        p = Env["_xclip"] = execute_pipes(
            "xclip", "-in", "-selection", "clipboard", universal_newlines=True
        )
        p.stdin.write(s)
        p.stdin.close()

    if CHECK.frontend("ht3.gui"):
        import ht3.gui

        @Env
        @cmd
        def MoveHtWindow():
            pass  # there is no proper Place

    class PaSinkInput(args.BaseParam):
        def get_sink_inputs(self):
            s = procio("pactl list sink-inputs")
            return re.findall(
                r'Sink Input #(\d+)(?:\n\t.*)*application.process.binary = "([^"]+)"', s
            )

        def complete(self, s):
            for id, name in self.get_sink_inputs():
                yield name

        def convert(self, s):
            for id, name in self.get_sink_inputs():
                if name == s:
                    return id
            return s

    class PaSink(args.BaseParam):
        def get_sink(self):
            s = procio("pactl list sinks")
            return re.findall(
                r'Sink #(\d+)(?:\n\t.*)*device.description = "([^"]+)"', s
            )

        def complete(self, s):
            for id, name in self.get_sink():
                yield name

        def convert(self, s):
            sinks = [
                (id, name)
                for (id, name) in self.get_sink()
                if s.lower() in name.lower()
            ]
            if len(sinks) > 1:
                raise ValueError("Search term too generic", s, sinks)
            if len(sinks) == 1:
                return sinks[0][0]
            return s

    @cmd
    def audio_move(sink_input: PaSinkInput(), sink: PaSink()):
        """Change which Sink a Pulse Audio Client uses"""

        cmd = f"pactl move-sink-input {sink_input} {sink}"
        show(cmd + ": " + procio(cmd))

    @cmd
    def screenshot(filename="~/tmp/screenshot.png"):
        if "/" in filename:
            path = pathlib.Path(filename).expanduser()
        else:
            path = pathlib.Path("~/tmp").expanduser() / filename

        subprocess.check_call(["import", "-silent", str(path)])
        subprocess.run(
            ["xclip", "-selection", "primary"], input=str(filename).encode("utf-8")
        )
        subprocess.check_call(
            ["xclip", "-selection", "clipboard", "-t", "image/png", str(path)]
        )
