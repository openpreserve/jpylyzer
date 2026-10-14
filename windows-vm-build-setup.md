# Windows 11 VM setup notes

This document describes how to set up a virtual machine for building Jpylyzer Windows binaries.

## Download Windows 11 IoT Enterprise LTSC ISO image

Available from [Microsoft](https://www.microsoft.com/en-us/evalcenter/download-windows-11-iot-enterprise-ltsc-eval). Microsoft offers a 90 day fully functional evaluation period, after which the software must be purchased. 

## Create QEMU disk image

Command:

```
qemu-img create -f qcow2 win11_jpylyzer.qcow2 32G
```

## Start QEMU

Command:

```
qemu-system-x86_64 -M q35,usb=on,acpi=on,hpet=off -m 6G -cpu host,hv_relaxed,hv_frequencies,hv_vpindex,hv_ipi,hv_tlbflush,hv_spinlocks=0x1fff,hv_synic,hv_runtime,hv_time,hv_stimer,hv_vapic -smp cores=4 -accel kvm -drive file=win11_jpylyzer.qcow2 -device usb-tablet -device VGA,vgamem_mb=256 -nic user,model=e1000 -monitor stdio -cdrom 26100.1742.240906-0331.ge_release_svc_refresh_CLIENT_IOT_LTSC_EVAL_x64FRE_en-us.iso
```

## Install Windows

Follow installation instructions from:

[How to install Windows 11 in QEMU](https://computernewb.com/wiki/QEMU/Guests/Windows_11)

Including "Local Setup". Note: command prompt can be started at any time with Shift-F10 (not just "immediately").

## Install Python

Separately install 64 and 32 bit versions of 3.14.8 (.exe installer, as MSIX installer doesn't support parallel installation of 64 and 32 bit versions). Locations:

- `C:\Python314`
- `C:\Python314-32`

No need to update any environment variables here, in the build script we'll explicitly point to the full paths.

## Install PyInstaller

Install for both 64 and 32 bit versions:

```
C:\Python314\python -m pip install pyinstaller
C:\Python314-32\python -m pip install pyinstaller
```

## Install Git

Download from [website](https://git-scm.com/).

## Install 7-zip

Install from [7-zip website](https://www.7-zip.org/)

Why this is needed - PowerShell's built-in ZIP function produces ZIP files that don't extract correctly on a Linux system.

## Set ExecutionPolicy

In order to run PowerShell scripts, enter the command: 

```
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

## Set up shared folder with host (requires Samba running on host)

Close VM, and start again using:

```
qemu-system-x86_64 -M q35,usb=on,acpi=on,hpet=off -m 6G -cpu host,hv_relaxed,hv_frequencies,hv_vpindex,hv_ipi,hv_tlbflush,hv_spinlocks=0x1fff,hv_synic,hv_runtime,hv_time,hv_stimer,hv_vapic -smp cores=4 -accel kvm -drive file=win11_jpylyzer.qcow2 -device usb-tablet -device VGA,vgamem_mb=256 -nic user,model=e1000 -monitor stdio -nic user,id=nic0,smb=/home/johan/shared
```

The (final) `-nic` option defines a shared Samba folder on the host (Linux) machine.

Map to network drive in Win explorer, using network location `\\10.0.2.2\shared`[^1].

## Clone Jpylyzer

```
git clone https://github.com/openpreserve/jpylyzer.git
cd jpylyzer
```

Optionally switch to latest dev branch:

```
git checkout 2-3-dev
git pull
```

# Further resources

- [How to install Windows 11 in QEMU](https://computernewb.com/wiki/QEMU/Guests/Windows_11)

[^1]: [This blog post](https://shallowsky.com/blog/linux/qemu-windows-file-share.html) mentions another location, but this didn't work for me. A quick search turned up [this thread](https://bbs.archlinux.org/viewtopic.php?id=302956), which mentions the alternative location.
