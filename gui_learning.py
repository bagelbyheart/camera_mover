#!/usr/bin/env python3

import wx

version = '0.0.2'


def camera_copy(src, dst, dup=False, destructive=False, dry_run=True):
    # this is a fake for testing purposes.
    out_string = (f"Source: {src}\n"
                  f"Target: {dst}\n"
                  f"skip_dups={dup}\n"
                  f"destructive={destructive}\n"
                  f"dry-run={dry_run}")
    print(out_string)
    list_counts = (2361, 10, 2361)
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
        btn_src = wx.Button(panel, -1, size=(30, -1), label="...")
        btn_src.Bind(wx.EVT_BUTTON, self.on_src)
        # target interfaces
        label_trg = wx.StaticText(panel, size=(90, -1),
                                  label="Target Directory")
        self.edit_trg = wx.TextCtrl(panel,
                                    style=wx.TE_READONLY, size=(240, -1))
        btn_trg = wx.Button(panel, -1, size=(30, -1), label="...")
        btn_trg.Bind(wx.EVT_BUTTON, self.on_trg)
        # options interfaces
        self.chk_dups = wx.CheckBox(panel, -1, label="Skip Duplicates")
        self.chk_dest = wx.CheckBox(panel, -1, label="Delete Sources")
        self.chk_dryr = wx.CheckBox(panel, -1, label="Dry Run")
        # confirmation interfaces
        self.btn_okay = wx.Button(panel, -1, "Copy")
        self.btn_okay.Bind(wx.EVT_BUTTON, self.on_okay)
        self.btn_okay.Disable()
        btn_cncl = wx.Button(panel, -1, "Cancel")
        btn_cncl.Bind(wx.EVT_BUTTON, self.on_cncl)
        # source sizer
        src_sizer = wx.BoxSizer(wx.HORIZONTAL)
        src_sizer.Add(label_src, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        src_sizer.Add(self.edit_src, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        src_sizer.Add(btn_src, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        # target sizer
        trg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        trg_sizer.Add(label_trg, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        trg_sizer.Add(self.edit_trg, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        trg_sizer.Add(btn_trg, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        # options sizer
        opt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        opt_sizer.Add(self.chk_dups, 0, 0, 0)
        opt_sizer.Add(self.chk_dest, 0, 0, 0)
        opt_sizer.Add(self.chk_dryr, 0, 0, 0)
        # confirmation sizer
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.btn_okay, 0, 0, 0)
        btn_sizer.Add(btn_cncl, 0, 0, 0)
        # top level sizer
        org_sizer = wx.BoxSizer(wx.VERTICAL)
        org_sizer.Add(src_sizer, 0, wx.ALL | wx.EXPAND, 5)
        org_sizer.Add(trg_sizer, 0, wx.ALL, 5)
        org_sizer.Add(opt_sizer, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        org_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        panel.SetSizer(org_sizer)

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
        camera_results = camera_copy(cam_source, cam_target, skip_dups,
                                     destructive, dry_run)
        output = (f'Files Processed: {camera_results[0]}\n'
                  f'Duplicates Skipped: {camera_results[1]}\n'
                  f'Files "Moved": {camera_results[2]}\n')
        wx.MessageBox(output, "Test Window", wx.OK | wx.ICON_INFORMATION)
        self.Close()

    def on_cncl(self, e):
        self.Close()


def main():
    win_title = "Camera Copy GUI"
    win_styles = wx.DEFAULT_DIALOG_STYLE
    app = wx.App()
    frame = MainFrame(None, size=(400, 170), style=win_styles, title=win_title)
    frame.Show()
    app.MainLoop()


main()
