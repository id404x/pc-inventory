"""Merge multiple per-host JSON reports into a single CSV summary."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

CSV_COLUMNS = [
    "hostname",
    "collected_at",
    "os_name",
    "os_version",
    "cpu_model",
    "cpu_cores_logical",
    "memory_total_mb",
    "disk_total_gb",
    "primary_ipv4",
    "primary_mac",
]


def _flatten(report: dict[str, Any]) -> dict[str, Any]:
    osd = report.get("os", {}) or {}
    cpu = report.get("cpu", {}) or {}
    mem = report.get("memory", {}) or {}
    disks = report.get("disks", []) or []
    nets = report.get("network", []) or []

    primary_net = nets[0] if nets else {}
    return {
        "hostname": report.get("hostname", ""),
        "collected_at": report.get("collected_at", ""),
        "os_name": osd.get("name", ""),
        "os_version": osd.get("version", ""),
        "cpu_model": cpu.get("model", ""),
        "cpu_cores_logical": cpu.get("cores_logical", 0),
        "memory_total_mb": mem.get("total_mb", 0),
        "disk_total_gb": sum(d.get("size_gb", 0) for d in disks),
        "primary_ipv4": primary_net.get("ipv4", ""),
        "primary_mac": primary_net.get("mac", ""),
    }


def merge_reports(report_paths: list[Path], output_csv: Path) -> int:
    rows: list[dict[str, Any]] = []
    for p in report_paths:
        try:
            data = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(_flatten(data))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
