#!/usr/bin/env python3

import hashlib
import argparse
import os
import shutil
import sys
import re
import exif
import time
import math

version = '0.4.0'

strftime = time.strftime
gmtime = time.gmtime


class HiddenPrints:
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr


def process_args():
    description = ("A tool to find all jpg images in a directory and copy them"
                   " to the destination directory with names based on exif "
                   "data.\n\nIt is recommended to run this against directories"
                   " where all images are from the same source.")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("source",
                        help="directory to search for jpg images")
    parser.add_argument("destination",
                        help="directory for sorted jpg images")
    parser.add_argument("--skip-dups", action="store_true",
                        help="check for and skip duplicate images")
    parser.add_argument("--dry-run", action="store_true",
                        help="provide an action list instead of copying files")
    parser.add_argument("--destructive", action="store_true",
                        help=("move jpg images instead of copying them\nthis "
                              "option will also delete duplicates when paired "
                              "with --skip-dups\nThis has no impact if "
                              "--dry-run has been set"))
    parser.add_argument("--error-name",
                        help=("provide a name to prepend to files when exif "
                              "data cannot be found"))
    return (parser.parse_args())


def char_squash(s, ch):
    # this was taken from stackoverflow and I don't fully understand it yet.
    new_str = []
    l = len(s)
    for i in range(len(s)):
        if (s[i] == ch and i != (l-1) and
           i != 0 and s[i + 1] != ch and s[i-1] != ch):
            new_str.append(s[i])
        elif s[i] == ch:
            if ((i != (l-1) and s[i + 1] == ch) and
               (i != 0 and s[i-1] != ch)):
                new_str.append(s[i])
        else:
            new_str.append(s[i])
    return ("".join(i for i in new_str))


def path_cleaner(in_str):
    invalid_chars = ("/", "<", ">", ":", '"', "\\", "|", "?", "*", ",", ".",
                     " ", "&", "%")
    for char in invalid_chars:
        in_str = char_squash(in_str.replace(char, "-"), "-")
    return (in_str)


def image_listing2(directory):
    listing = []
    for p, d, f in os.walk(directory):
        for file in f:
            if re.match(".*(JP|jp)((eg|EG)|G|g)$", file):
                full_path = os.path.join(p, file)
                listing.append(full_path)
    return (listing)


def exif_parse2(file_content):
    exif_object = exif.Image(file_content)
    if exif_object.has_exif:
        with HiddenPrints():
            exif_dict = exif_object.get_all()
        return (exif_dict)
    else:
        return (1)


def name_gen2(image, exif_dict):
    try:
        make = exif_dict['make']
    except:
        make = "brand"
    try:
        model = exif_dict['model']
    except:
        model = "camera"
    try:
        date = exif_dict['datetime'].replace(":", "-").replace(" ", "T")
    except:
        date = strftime("%Y-%m-%dT%H-%M-%S", gmtime(os.path.getmtime(image)))
    name = path_cleaner("_".join((make, model, date)))
    return (name)


def dup_check(name, md5_hashes):
    with open(name, 'rb') as image:
        content = image.read()
        content_hash = hashlib.md5(content).hexdigest()
    try:
        if md5_hashes[content_hash]:
            return_code = content_hash
    except KeyError:
        return_code = 0
        md5_hashes[content_hash] = name
    return (return_code)


def dup_check2(name, content, md5_hashes):
    content_hash = hashlib.md5(content).hexdigest()
    try:
        if md5_hashes[content_hash]:
            return_code = content_hash
    except KeyError:
        return_code = 0
        md5_hashes[content_hash] = name
    return (return_code)


def name_check(name, name_bases):
    try:
        name_bases[name] += 1
    except KeyError:
        name_bases[name] = 1
    count = name_bases[name]
    name = "_".join((name, str(count).rjust(3, "0")))
    name = name + ".jpg"
    return (name)


def action_parser(image, out_name, destination, destructive):
    src_action = "copy"
    dup_action = "ignore"
    if destructive:
        src_action = "move"
        dup_action = "delete"
    dry_name = os.path.join(destination, "camera_copy.csv")
    full_name = os.path.join(destination, out_name)
    if dry_run:
        with open(dry_name, "+a") as out_file:
            if "DUP of" in out_name:
                out_file.write(f'"{dup_action}","{image}"\n')
            else:
                out_file.write(f'"{src_action}","{image}","{full_name}"\n')
    else:
        if "DUP of" in out_name:
            if dup_action == "delete":
                os.remove(image)
        else:
            if src_action == "move":
                shutil.move(image, full_name)
            else:
                shutil.copy(image, full_name)


def list_review(image_list, check_dup, destination, destructive):
    name_bases = {}
    dup_list = {}
    conv_list = {}
    item_count = 0
    dup_count = 0
    item_total = len(image_list)
    for image in image_list:
        item_count += 1
        percent = math.floor((item_count / item_total) * 100)
        print(f"Processing: {item_count} of {item_total}"
              f"({percent}%)", end="\r")
        with open(image, "rb") as image_handle:
            image_content = image_handle.read()
        if check_dup:
            dup_val = dup_check2(image, image_content, dup_list)
            if dup_val == 0:
                # this chunk seems ripe for functionalizing
                exif_data = exif_parse2(image_content)
                if exif_data != 1:
                    base_name = name_gen2(image, exif_data)
                    out_name = name_check(base_name, name_bases)
                else:
                    mod_time = strftime("%Y-%m-%dT%H-%M-%S",
                                        gmtime(os.path.getmtime(image)))
                    base_name = "bad_exif_" + mod_time
                    out_name = name_check(base_name, name_bases)
            else:
                dup_count += 1
                out_name = f"DUP of {dup_list[dup_val]}"
        else:
            # this chunk is a copy of the last chunk
            exif_data = exif_parse2(image_content)
            if exif_data != 1:
                base_name = name_gen2(image, exif_data)
                out_name = name_check(base_name, name_bases)
            else:
                mod_time = strftime("%Y-%m-%dT%H-%M-%S",
                                    gmtime(os.path.getmtime(image)))
                base_name = "bad_exif_" + mod_time
                out_name = name_check(base_name, name_bases)
        conv_list[image] = out_name
        action_parser(image, out_name, destination, destructive)
    print(f"")
    return (item_count, dup_count, len(conv_list))


def camera_copy(src, dst, dup=False, destructive=False, dry_run=True):
    images = image_listing2(src)
    if dry_run:
        dry_name = os.path.join(dst, "camera_copy.csv")
        with open(dry_name, "w") as out_file:
            out_file.write(f'\r')
    list_counts = list_review(images, dup, dst, destructive)
    return (list_counts)


def main():
    global dry_run
    global src_action
    global dup_action
    global source
    global destination
    args = process_args()
    source = args.source
    check_dupes = args.skip_dups
    dry_run = args.dry_run
    destructive = args.destructive
    destination = args.destination
    camera_results = camera_copy(source, destination, check_dupes, destructive,
                                 dry_run)
    output = (f'Files Processed: {camera_results[0]}\n'
              f'Duplicates Skipped: {camera_results[1]}\n'
              f'Files "Moved": {camera_results[2]}\n')
    print(output)
    return (0)


try:
    main()
except (BrokenPipeError, KeyboardInterrupt):
    blob = True
