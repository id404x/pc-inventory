"""CLI: `python -m pc_inventory ...`."""

from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

from .collect import collect_report
from .merge import merge_reports


def _cmd_collect(args: argparse.Namespace) -> int:
    report = collect_report()
    if args.output:
        out_path = Path(args.output)
    else:
        out_dir = Path.home() / ".pc-inventory"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{socket.gethostname()}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"saved {out_path}")
    return 0


def _cmd_merge(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.inputs]
    out = Path(args.output)
    n = merge_reports(paths, out)
    print(f"merged {n} reports into {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pc-inventory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_collect = sub.add_parser("collect", help="Collect report from this machine")
    p_collect.add_argument("--output", "-o", help="Output JSON path")
    p_collect.set_defaults(func=_cmd_collect)

    p_merge = sub.add_parser("merge", help="Merge JSON reports into CSV")
    p_merge.add_argument("inputs", nargs="+", help="Paths to per-host JSON reports")
    p_merge.add_argument("--output", "-o", default="inventory.csv", help="Output CSV path")
    p_merge.set_defaults(func=_cmd_merge)

    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
