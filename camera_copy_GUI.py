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
import wx

version = '1.0.2'
global dry_run


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


def image_listing2(directory, frame):
    listing = []
    for p, d, f in os.walk(directory):
        for file in f:
            wx.Yield()
            if re.match(".*(JP|jp)((eg|EG)|G|g)$", file):
                full_path = os.path.join(p, file)
                listing.append(full_path)
                process_out = (f"Enumerating: {len(listing)}")
                frame.sts_details.SetLabel(process_out)
    return (listing)


def exif_parse2(file_content):
    try:
        exif_object = exif.Image(file_content)
        if exif_object.has_exif:
            with HiddenPrints():
                exif_dict = exif_object.get_all()
            return (exif_dict)
        else:
            return (1)
    except ValueError:
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


def action_parser(image, out_name, destination, destructive, dry_run):
    src_action = "copy"
    dup_action = "ignore"
    if destructive:
        src_action = "move"
        dup_action = "delete"
    dry_name = os.path.join(destination, "camera_copy.csv")
    full_name = os.path.join(destination, out_name)
    if dry_run:
        with open(dry_name, "+a", encoding="utf-8") as out_file:
            if "DUP of" in out_name:
                out_file.write(f'"{dup_action}","{image}","{out_name}"\n')
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


def list_review(image_list, check_dup, destination, destructive, dry, frame):
    name_bases = {}
    dup_list = {}
    conv_list = {}
    item_count = 0
    dup_count = 0
    item_total = len(image_list)
    for image in image_list:
        # print(image)
        item_count += 1
        percent = math.floor((item_count / item_total) * 100)
        process_out = (f"Processing: {item_count} of "
                       f"{item_total} ({percent}%)\r")
        frame.sts_details.SetLabel(process_out)
        wx.Yield()
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
        action_parser(image, out_name, destination, destructive, dry)
    return (item_count, dup_count, len(conv_list))


def camera_copy(src, dst, frame, dup=False, destructive=False, dry_run=True):
    images = image_listing2(src, frame)
    if dry_run:
        dry_name = os.path.join(dst, "camera_copy.csv")
        with open(dry_name, "w", encoding="utf-8") as out_file:
            out_file.write(f'"action","source","destination"\n')
    list_counts = list_review(images, dup, dst, destructive, dry_run, frame)
    return (list_counts)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)
        panel = wx.Panel(self)
        # source interfaces
        label_src = wx.StaticText(panel, size=(90, -1),
                                  label="Source Directory")
        self.edit_src = wx.TextCtrl(panel,
                                    style=wx.TE_READONLY, size=(240, -1))
        self.btn_src = wx.Button(panel, -1, size=(30, -1), label="...")
        self.btn_src.Bind(wx.EVT_BUTTON, self.on_src)
        # target interfaces
        label_trg = wx.StaticText(panel, size=(90, -1),
                                  label="Target Directory")
        self.edit_trg = wx.TextCtrl(panel,
                                    style=wx.TE_READONLY, size=(240, -1))
        self.btn_trg = wx.Button(panel, -1, size=(30, -1), label="...")
        self.btn_trg.Bind(wx.EVT_BUTTON, self.on_trg)
        # options interfaces
        self.chk_dups = wx.CheckBox(panel, -1, label="Skip Duplicates")
        self.chk_dest = wx.CheckBox(panel, -1, label="Delete Sources")
        self.chk_dryr = wx.CheckBox(panel, -1, label="Dry Run")
        # status interface
        # self.sts_box = wx.StaticBox(panel, -1, "Status:", size=(380, 80))
        self.sts_details = wx.StaticText(panel, -1, "Ready", size=(380, 20))
        # confirmation interfaces
        self.btn_okay = wx.Button(panel, -1, "Copy")
        self.btn_okay.Bind(wx.EVT_BUTTON, self.on_okay)
        self.btn_okay.Disable()
        self.btn_cncl = wx.Button(panel, -1, "Exit")
        self.btn_cncl.Bind(wx.EVT_BUTTON, self.on_cncl)
        # source sizer
        src_sizer = wx.BoxSizer(wx.HORIZONTAL)
        src_sizer.Add(label_src, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        src_sizer.Add(self.edit_src, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        src_sizer.Add(self.btn_src, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        # target sizer
        trg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        trg_sizer.Add(label_trg, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        trg_sizer.Add(self.edit_trg, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        trg_sizer.Add(self.btn_trg, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        # options sizer
        opt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        opt_sizer.Add(self.chk_dups, 0, 0, 0)
        opt_sizer.Add(self.chk_dest, 0, 0, 0)
        opt_sizer.Add(self.chk_dryr, 0, 0, 0)
        # status_sizer
        sts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sts_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, panel, "Status:")
        sts_sizer.Add(self.sts_details, 0, 0, 0)
        # confirmation sizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.btn_okay, 0, 0, 0)
        btn_sizer.Add(self.btn_cncl, 0, 0, 0)
        # top level sizer
        org_sizer = wx.BoxSizer(wx.VERTICAL)
        org_sizer.Add(src_sizer, 0, wx.ALL | wx.EXPAND, 5)
        org_sizer.Add(trg_sizer, 0, wx.ALL, 5)
        org_sizer.Add(opt_sizer, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        org_sizer.Add(sts_sizer, 0, wx.ALL, 5)
        org_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        panel.SetSizer(org_sizer)

    def toggleUI(self, status=False):
        if status:
            self.btn_okay.Disable()
            self.btn_cncl.Disable()
            self.btn_src.Disable()
            self.btn_trg.Disable()
            self.chk_dest.Disable()
            self.chk_dups.Disable()
            self.chk_dryr.Disable()
        else:
            self.btn_okay.Enable()
            self.btn_cncl.Enable()
            self.btn_src.Enable()
            self.btn_trg.Enable()
            self.chk_dest.Enable()
            self.chk_dups.Enable()
            self.chk_dryr.Enable()

    def on_src(self, e):
        self.edit_src.SetValue(wx.DirSelector("Choose a source directory"))
        src_path = self.edit_src.GetValue()
        trg_path = self.edit_trg.GetValue()
        if src_path != '' and trg_path != '':
            self.btn_okay.Enable()

    def on_trg(self, e):
        self.edit_trg.SetValue(wx.DirSelector("Choose a target directory"))
        src_path = self.edit_src.GetValue()
        trg_path = self.edit_trg.GetValue()
        if src_path != '' and trg_path != '':
            self.btn_okay.Enable()

    def on_okay(self, e):
        self.toggleUI(True)
        cam_source = self.edit_src.GetValue()
        cam_target = self.edit_trg.GetValue()
        skip_dups = self.chk_dups.GetValue()
        destructive = self.chk_dest.GetValue()
        dry_run = self.chk_dryr.GetValue()
        out_string = (f"Source: {cam_source}\n"
                      f"Target: {cam_target}\n"
                      f"skip_dups={skip_dups}\n"
                      f"destructive={destructive}\n"
                      f"dry-run={dry_run}")
        camera_results = camera_copy(cam_source, cam_target, self, skip_dups,
                                     destructive, dry_run)
        output = (f'Files Processed: {camera_results[0]}\n'
                  f'Duplicates Skipped: {camera_results[1]}\n'
                  f'Files "Moved": {camera_results[2]}\n')
        wx.MessageBox(output, "Results", wx.OK | wx.ICON_INFORMATION)
        process_out = (f"Processed: {camera_results[0]} of "
                       f"{camera_results[0]} (100%)\r")
        self.sts_details.SetLabel(process_out)
        self.toggleUI()

    def on_cncl(self, e):
        self.Close()


def main():
    win_title = "Camera Copy GUI"
    win_styles = wx.DEFAULT_DIALOG_STYLE
    app = wx.App(False)
    frame = MainFrame(None, size=(400, 215), style=win_styles, title=win_title)
    # this is going to be replaced with some base64 tomfoolery
    # 1. store the icon as a giant base64 string
    # 2. decode that to a temp file
    # 3. read that temp file below
    # 4. then delete it
    # for now, no icon.
    # frame.SetIcon(wx.Icon("travellers.ico"))
    frame.Show()
    app.MainLoop()


main()
