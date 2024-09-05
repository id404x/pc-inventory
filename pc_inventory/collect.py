"""Collect a hardware/software report from the current machine."""

from __future__ import annotations

import platform
import socket
import time
from datetime import datetime
from typing import Any

import psutil

try:
    import distro as _distro
except ImportError:
    _distro = None


def _os_info() -> dict[str, Any]:
    name = platform.system()
    version = platform.release()
    if _distro is not None and name.lower() == "linux":
        name = _distro.name(pretty=False) or name
        version = _distro.version(pretty=False) or version
    boot = psutil.boot_time()
    return {
        "name": name,
        "version": version,
        "kernel": platform.release(),
        "uptime_sec": max(0, int(time.time() - boot)),
    }


def _cpu_info() -> dict[str, Any]:
    freq = psutil.cpu_freq()
    return {
        "model": platform.processor() or "unknown",
        "cores_physical": psutil.cpu_count(logical=False) or 0,
        "cores_logical": psutil.cpu_count(logical=True) or 0,
        "freq_max_mhz": int(freq.max) if freq else 0,
    }


def _memory_info() -> dict[str, Any]:
    vm = psutil.virtual_memory()
    return {
        "total_mb": vm.total // (1024 * 1024),
        "available_mb": vm.available // (1024 * 1024),
    }


def _disks_info() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            size_gb = int(usage.total / (1024**3))
        except (PermissionError, OSError):
            size_gb = 0
        out.append(
            {
                "device": part.device,
                "size_gb": size_gb,
                "fstype": part.fstype,
                "mountpoint": part.mountpoint,
            }
        )
    return out


def _network_info() -> list[dict[str, Any]]:
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    out: list[dict[str, Any]] = []
    for iface, addr_list in addrs.items():
        mac = ""
        ipv4 = ""
        for a in addr_list:
            family = getattr(a, "family", None)
            if family == psutil.AF_LINK:
                mac = a.address
            elif family == socket.AF_INET:
                ipv4 = a.address
        st = stats.get(iface)
        if st and not st.isup:
            continue
        out.append(
            {
                "name": iface,
                "mac": mac,
                "ipv4": ipv4,
                "mtu": st.mtu if st else 0,
            }
        )
    return out


def collect_report() -> dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "collected_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "os": _os_info(),
        "cpu": _cpu_info(),
        "memory": _memory_info(),
        "disks": _disks_info(),
        "network": _network_info(),
    }
