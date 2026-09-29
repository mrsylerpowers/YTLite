#!/usr/bin/env python3
"""Remove paid-subscription wording from the tweak bundle inside a built IPA.

The released tweak debs carry an orphan "FeaturesNotActivated" string
("You are not logged in. To access YouTube Plus features, please log in with an
active subscription."). Nothing in the tweak references it, so dropping it only
removes subscription wording from the shipped app.

The IPA is rewritten entry-for-entry rather than appended to, so no duplicate
entries can appear in the archive.

Usage: strip_subscription_strings.py <ipa>
"""
import os
import plistlib
import re
import sys
import zipfile

BLOCKED_KEYS = {"FeaturesNotActivated"}
REPORT_ONLY = re.compile(r"active subscription|subscription status|subscription level", re.I)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    ipa = sys.argv[1]

    with zipfile.ZipFile(ipa) as archive:
        targets = [n for n in archive.namelist()
                   if n.endswith(".lproj/Localizable.strings") and "YTLite.bundle" in n]
        if not targets:
            print("no YTLite.bundle localization files in the IPA")
            return 1

        replacements = {}
        removed = 0
        for name in targets:
            strings = plistlib.loads(archive.read(name))
            dirty = False
            for key in list(strings):
                value = str(strings[key])
                if key in BLOCKED_KEYS:
                    del strings[key]
                    removed += 1
                    dirty = True
                elif REPORT_ONLY.search(value):
                    print(f"NOTE: still present in {name}: {key} = {value}")
            if dirty:
                replacements[name] = plistlib.dumps(strings, fmt=plistlib.FMT_BINARY)

        if not replacements:
            print("nothing to remove")
            return 0

        tmp = ipa + ".rewrite"
        with zipfile.ZipFile(tmp, "w") as out:
            for info in archive.infolist():
                data = replacements.get(info.filename) or archive.read(info.filename)
                new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                new_info.compress_type = info.compress_type
                new_info.external_attr = info.external_attr
                new_info.internal_attr = info.internal_attr
                new_info.create_system = info.create_system
                out.writestr(new_info, data)

    os.replace(tmp, ipa)
    print(f"removed {removed} subscription strings across {len(replacements)} of {len(targets)} localizations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
