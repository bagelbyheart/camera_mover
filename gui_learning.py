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


class ErrorFrame(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(ErrorFrame, self).__init__(*args, **kw)
        panel = wx.Panel(self)
        self.sts_details = wx.TextCtrl(panel, -1, "Empty", style=wx.TE_READONLY | wx.TE_MULTILINE, size=(780, 265))
        sts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sts_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, panel, "Exception Details")
        sts_sizer.Add(self.sts_details, 0, wx.LEFT, 5)
        errormsg = wx.StaticText(panel, -1, "Exceptions were encountered. Please copy the details below to report issues.")
        btn_cncl = wx.Button(panel, -1, "Exit")
        btn_cncl.Bind(wx.EVT_BUTTON, self.on_cncl)
        org_sizer = wx.BoxSizer(wx.VERTICAL)
        org_sizer.Add(errormsg, 0, wx.ALL, 5)
        org_sizer.Add(sts_sizer, 0, wx.ALL, 5)
        org_sizer.Add(btn_cncl, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        panel.SetSizer(org_sizer)

    def on_cncl(self, e):
        self.Close()

    def pass_text(self, str):
        self.sts_details.SetValue(str)


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


test_output = """
{'KeyError': {'count': 48,
              'files': ['Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-09-10T16-06-52_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-09-10T16-06-52_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-09-10T16-06-52_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-13T12-44-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-13T12-44-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-13T12-44-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T02-48-54_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T02-48-54_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T02-48-54_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-25-50_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-25-50_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-25-50_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-26-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-26-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-14T13-26-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-17T03-16-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-17T03-16-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-10-17T03-16-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T00-53-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T00-53-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T00-53-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T16-06-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T16-06-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-11-06T16-06-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T20-57-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T20-57-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T20-57-00_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-06_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-12T21-54-10_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-29T21-54-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-29T21-54-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2020-12-29T21-54-24_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-07T13-46-20_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-07T13-46-20_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-07T13-46-20_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-08T03-42-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-08T03-42-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-08T03-42-34_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-09T02-30-40_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-09T02-30-40_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-01-09T02-30-40_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-02-08T08-43-36_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-02-08T08-43-36_001.jpg',
                        'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\brand_camera_2021-02-08T08-43-36_001.jpg']},
 'plum.exceptions.UnpackError': {'count': 8,
                                 'files': ['Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2020-10-04T13-35-12_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2020-10-04T13-35-14_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2020-10-05T23-23-24_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2020-10-05T23-23-28_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2020-10-27T21-14-32_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2021-02-16T08-30-16_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2021-03-06T19-25-28_001.jpg',
                                           'Y:\\BeanMEDIA\\Sorted_Photo_Pass\\bad_exif_2021-03-14T17-05-48_001.jpg']}}
"""

def main():
    win_title = "Camera Copy GUI"
    win_styles = wx.DEFAULT_DIALOG_STYLE
    app = wx.App()
    frame = ErrorFrame(None, size=(800, 400), style=win_styles, title=win_title)
    frame.pass_text(test_output)
    frame.Show()
    app.MainLoop()


main()
