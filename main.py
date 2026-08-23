# -*- coding: utf-8 -*-

import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.clock import Clock

import arabic_reshaper

# برای اندروید: ماژول فعالیت
if platform == "android":
    from android import activity as android_activity
    from jnius import autoclass, cast

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Intent = autoclass("android.content.Intent")
    Context = autoclass("android.content.Context")


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


# 📁 فونت فارسی
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
        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        title = PersianLabel(text="ضبط صفحه گوشی (اندروید 15)", font_size="24sp")
        info = PersianLabel(text="جهت شروع، اجازه ضبط صفحه را تأیید کنید.", font_size="16sp")
        start_button = PersianButton(text="🎥 شروع ضبط صفحه", font_size="18sp", size_hint_y=None, height=65)
        stop_button = PersianButton(text="⏹ توقف ضبط", font_size="18sp", size_hint_y=None, height=65)
        photo_button = PersianButton(text="📸 عکس از صفحه", font_size="18sp", size_hint_y=None, height=65)

        start_button.bind(on_press=self.start_recording)
        stop_button.bind(on_press=self.stop_recording)
        photo_button.bind(on_press=self.take_screenshot)

        layout.add_widget(title)
        layout.add_widget(info)
        layout.add_widget(start_button)
        layout.add_widget(stop_button)
        layout.add_widget(photo_button)

        # ثبت callback برای دریافت نتیجه مجوز
        if platform == "android":
            android_activity.bind(on_activity_result=self.on_activity_result)

        return layout

    def on_activity_result(self, request_code, result_code, data):
        """دریافت نتیجه درخواست مجوز MediaProjection"""
        if request_code == 1001 and result_code == -1:  # RESULT_OK = -1
            self.start_service_with_permission(data)

    def start_service_with_permission(self, data):
        """سرویس ضبط را با اطلاعات مجوز شروع می‌کند"""
        try:
            activity = PythonActivity.mActivity
            service_intent = Intent(activity, autoclass("org.example.screenrecorder.ScreenCaptureService"))
            # داده‌های مجوز
            service_intent.putExtra("resultCode", -1)  # RESULT_OK
            service_intent.putExtra("data", data)
            # ابعاد صفحه (می‌توانید از display metrics بگیرید، این‌جا ساده‌سازی شد)
            service_intent.putExtra("width", 720)
            service_intent.putExtra("height", 1280)
            service_intent.putExtra("density", 320)
            activity.startService(service_intent)
            print("سرویس ضبط شروع شد.")
        except Exception as e:
            print("خطا در شروع سرویس:", e)

    def start_recording(self, instance):
        if platform != "android":
            print("این بخش فقط داخل اندروید اجرا می‌شود.")
            return
        try:
            activity = PythonActivity.mActivity
            MediaProjectionManager = autoclass("android.media.projection.MediaProjectionManager")
            projection_service = activity.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
            mgr = cast(MediaProjectionManager, projection_service)
            intent = mgr.createScreenCaptureIntent()
            activity.startActivityForResult(intent, 1001)
        except Exception as e:
            print("خطا در درخواست مجوز:", e)

    def stop_recording(self, instance):
        if platform != "android":
            return
        try:
            activity = PythonActivity.mActivity
            service_intent = Intent(activity, autoclass("org.example.screenrecorder.ScreenCaptureService"))
            activity.stopService(service_intent)
            print("سرویس ضبط متوقف شد.")
        except Exception as e:
            print("خطا در توقف سرویس:", e)

    def take_screenshot(self, instance):
        if platform != "android":
            print("درخواست عکس از صفحه (روی ویندوز فعال نیست)")
            return
        print("قابلیت عکس از صفحه هنوز پیاده‌سازی نشده است.")


if __name__ == "__main__":
    ScreenRecorderApp().run()
