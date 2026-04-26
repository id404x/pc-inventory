# pc-inventory

Small CLI I put together while inventorying a couple of small offices and
a PC club. Nobody wanted to pay for a real RMM, so this just walks one
machine and dumps its specs to JSON. Run it on every box, drop the JSONs
in one folder, then merge them into a CSV that a non-technical person
(an accountant, in my case) can read.

No agent, nothing persistent. Just `psutil` doing the heavy lifting and
`distro` for nicer Linux names.

## Use

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m pc_inventory collect                          (writes ~/.pc-inventory/<host>.json)
python3 -m pc_inventory collect -o reports/lab1.json     (custom path)

python3 -m pc_inventory merge reports/*.json -o inventory.csv
```

There's an `example_report.json` in the repo so you know roughly what
the output looks like before running it.

The merge step picks the first up-state network interface for the CSV
summary — the accountant only cared about one IP/MAC per machine and
having every Wi-Fi/Bluetooth/loopback in the table just made it noisy.
If you need everything, the raw per-host JSON keeps it all.

Tested on Ubuntu, Debian, and Windows 10/11. macOS should work too but
I haven't actually verified.

License: MIT.
