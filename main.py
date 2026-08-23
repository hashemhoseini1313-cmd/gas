# -*- coding: utf-8 -*-

import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import platform

import arabic_reshaper

if platform == "android":
    from android import activity as android_activity
    from jnius import autoclass, cast

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Intent = autoclass("android.content.Intent")
    Context = autoclass("android.content.Context")
    Build = autoclass("android.os.Build")   # ← اضافه شد


def ftext(text):
    """اصلاح چسبندگی حروف، معکوس‌سازی و اصلاح هوشمند جابه‌جایی پرانتزها"""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    swapped = []
    for char in reshaped_text:
        if char == '(':
            swapped.append(')')
        elif char == ')':
            swapped.append('(')
        else:
            swapped.append(char)
    temp_text = "".join(swapped)
    reversed_text = temp_text[::-1]
    return re.sub(r'\d+', lambda m: m.group(0)[::-1], reversed_text)


if platform == "android":
    FONT_FILE = "fonts/Vazirmatn-Light.ttf"
else:
    FONT_FILE = "C:\\Windows\\Fonts\\arial.ttf"
LabelBase.register(name="PersianFont", fn_regular=FONT_FILE)


class PersianLabel(Label):
    def __init__(self, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = ftext(kwargs["text"])
        kwargs.setdefault("font_name", "PersianFont")
        kwargs.setdefault("halign", "right")
        kwargs.setdefault("text_size", (None, None))
        super().__init__(**kwargs)

    def on_size(self, *args):
        self.text_size = (self.width, None)


class PersianButton(Button):
    def __init__(self, **kwargs):
        if "text" in kwargs:
            kwargs["text"] = ftext(kwargs["text"])
        kwargs.setdefault("font_name", "PersianFont")
        kwargs.setdefault("halign", "center")
        super().__init__(**kwargs)


class ScreenRecorderApp(App):
    def build(self):
        self.status_label = PersianLabel(
            text="آماده",
            font_size="16sp"
        )

        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        title = PersianLabel(text="ضبط صفحه گوشی (اندروید 15)", font_size="24sp")
        start_button = PersianButton(text="🎥 شروع ضبط صفحه", font_size="18sp", size_hint_y=None, height=65)
        stop_button = PersianButton(text="⏹ توقف ضبط", font_size="18sp", size_hint_y=None, height=65)
        photo_button = PersianButton(text="📸 عکس از صفحه", font_size="18sp", size_hint_y=None, height=65)

        start_button.bind(on_press=self.start_recording)
        stop_button.bind(on_press=self.stop_recording)
        photo_button.bind(on_press=self.take_screenshot)

        layout.add_widget(title)
        layout.add_widget(self.status_label)
        layout.add_widget(start_button)
        layout.add_widget(stop_button)
        layout.add_widget(photo_button)

        if platform == "android":
            android_activity.bind(on_activity_result=self.on_activity_result)

        return layout

    def on_activity_result(self, request_code, result_code, data):
        if request_code == 1001:
            if result_code == -1:  # RESULT_OK
                self.status_label.text = ftext("مجوز گرفته شد، در حال شروع سرویس...")
                self.start_service_with_permission(data)
            else:
                self.status_label.text = ftext("مجوز رد شد")

    def start_service_with_permission(self, data):
        try:
            activity = PythonActivity.mActivity
            service_intent = Intent(activity, autoclass("org.example.screenrecorder.ScreenCaptureService"))
            service_intent.putExtra("resultCode", -1)
            # ✅ اصلاح: cast به Parcelable
            service_intent.putExtra("data", cast('android.os.Parcelable', data))
            service_intent.putExtra("width", 720)
            service_intent.putExtra("height", 1280)
            service_intent.putExtra("density", 320)

            # ✅ اصلاح: استفاده از Build.VERSION.SDK_INT
            if Build.VERSION.SDK_INT >= 26:
                activity.startForegroundService(service_intent)
            else:
                activity.startService(service_intent)

            self.status_label.text = ftext("سرویس شروع شد")
        except Exception as e:
            self.status_label.text = ftext(f"خطا در شروع سرویس: {e}")

    def start_recording(self, instance):
        if platform != "android":
            self.status_label.text = ftext("فقط روی اندروید")
            return
        try:
            activity = PythonActivity.mActivity
            MediaProjectionManager = autoclass("android.media.projection.MediaProjectionManager")
            projection_service = activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
            mgr = cast(MediaProjectionManager, projection_service)
            intent = mgr.createScreenCaptureIntent()
            activity.startActivityForResult(intent, 1001)
            self.status_label.text = ftext("منتظر تأیید مجوز...")
        except Exception as e:
            self.status_label.text = ftext(f"خطا در درخواست مجوز: {e}")

    def stop_recording(self, instance):
        if platform != "android":
            return
        try:
            activity = PythonActivity.mActivity
            service_intent = Intent(activity, autoclass("org.example.screenrecorder.ScreenCaptureService"))
            activity.stopService(service_intent)
            self.status_label.text = ftext("سرویس متوقف شد")
        except Exception as e:
            self.status_label.text = ftext(f"خطا در توقف سرویس: {e}")

    def take_screenshot(self, instance):
        if platform != "android":
            self.status_label.text = ftext("قابلیت عکس فقط روی اندروید")
            return
        self.status_label.text = ftext("عکس از صفحه هنوز پیاده‌سازی نشده")


if __name__ == "__main__":
    ScreenRecorderApp().run()
