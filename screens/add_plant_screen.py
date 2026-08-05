"""
صفحه افزودن گیاه جدید
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.ui_components import COLORS, AdBanner, GreenButton


class AddPlantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, dt):
        root = FloatLayout()
        with root.canvas.before:
            Color(*COLORS['background'])
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                  size=lambda i, v: setattr(bg, 'size', v))

        # هدر
        header = BoxLayout(orientation='horizontal', size_hint=(1, None),
                           height=dp(60), padding=[dp(10), dp(8)],
                           pos_hint={'top': 1})
        with header.canvas.before:
            Color(*COLORS['primary'])
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', v),
                    size=lambda i, v: setattr(hbg, 'size', v))
        back_btn = Button(text='←', font_size=sp(22), size_hint=(None, 1),
                          width=dp(44), background_normal='',
                          background_color=[0, 0, 0, 0], color=COLORS['white'])
        back_btn.bind(on_press=lambda x: self.app.go_to_screen('plant_list', 'right'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='➕ افزودن گیاه جدید', font_size=sp(18),
                                bold=True, color=COLORS['white'], halign='right'))

        scroll = ScrollView(size_hint=(1, None))
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=dp(10), padding=[dp(14), dp(14)])
        content.bind(minimum_height=content.setter('height'))

        # آیکون
        icon_box = BoxLayout(size_hint_y=None, height=dp(80))
        icon_box.add_widget(Label(text='🌿', font_size=sp(60), halign='center'))
        content.add_widget(icon_box)

        # فیلدها
        fields = [
            ('نام فارسی گیاه *', 'مثلاً: سانسوریا', 'name', False),
            ('نام علمی', 'مثلاً: Sansevieria trifasciata', 'scientific_name', False),
            ('توضیحات', 'توضیح مختصری درباره گیاه...', 'description', True),
            ('شرایط رشد', 'نور، دما، رطوبت...', 'growth_conditions', True),
            ('مشکلات رایج', 'بیماری‌ها، آفات...', 'common_problems', True),
            ('روش درمان', 'نحوه رفع مشکلات...', 'treatment', True),
        ]
        self._inputs = {}
        for label, hint, key, multiline in fields:
            content.add_widget(self._make_field(label, hint, key, multiline))

        # اسپینرها
        spinners_data = [
            ('دسته‌بندی', 'category', ['آپارتمانی', 'گلدار', 'دارویی', 'درخت میوه']),
            ('نیاز به نور', 'light', ['کم', 'متوسط', 'زیاد', 'کم تا متوسط', 'متوسط تا زیاد']),
            ('میزان آبیاری', 'watering', ['کم', 'متوسط', 'زیاد', 'کم تا متوسط']),
            ('سطح نگهداری', 'care_level', ['بسیار آسان', 'آسان', 'متوسط', 'سخت']),
            ('محدوده قیمت', 'price_range', ['ارزان', 'مناسب', 'نسبتاً گران', 'گران']),
        ]
        for label, key, values in spinners_data:
            content.add_widget(self._make_spinner_field(label, key, values))

        # دکمه ذخیره
        save_btn = GreenButton(text='💾 ذخیره گیاه')
        save_btn.bind(on_press=self._save_plant)
        content.add_widget(save_btn)
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        scroll.add_widget(content)
        ad = AdBanner(size_hint=(None, None), size=(dp(300), dp(30)),
                      pos_hint={'center_x': 0.5})

        root.add_widget(scroll)
        root.add_widget(header)
        root.add_widget(ad)
        self.add_widget(root)

        def _fix(*a):
            scroll.pos = (0, dp(30))
            scroll.height = self.height - dp(60) - dp(30)
            ad.pos = (self.width / 2 - dp(150), 0)
        Clock.schedule_once(_fix, 0.05)

    def _make_field(self, label_text, hint, key, multiline):
        outer = BoxLayout(orientation='vertical', size_hint_y=None,
                          height=dp(90) if multiline else dp(72), spacing=dp(4))
        lbl = Label(text=label_text, font_size=sp(13), color=COLORS['text_primary'],
                    size_hint_y=None, height=dp(24), halign='right')
        lbl.bind(size=lbl.setter('text_size'))

        inp = TextInput(
            hint_text=hint, font_size=sp(13), multiline=multiline,
            size_hint_y=None, height=dp(60) if multiline else dp(42),
            background_color=get_color_from_hex('#F1F8E9'),
            foreground_color=COLORS['text_dark'],
            hint_text_color=get_color_from_hex('#A5D6A7'),
            halign='right',
        )
        self._inputs[key] = inp
        outer.add_widget(lbl)
        outer.add_widget(inp)
        return outer

    def _make_spinner_field(self, label_text, key, values):
        outer = BoxLayout(orientation='vertical', size_hint_y=None,
                          height=dp(68), spacing=dp(4))
        lbl = Label(text=label_text, font_size=sp(13), color=COLORS['text_primary'],
                    size_hint_y=None, height=dp(24), halign='right')
        lbl.bind(size=lbl.setter('text_size'))
        sp_widget = Spinner(text=values[0], values=values, size_hint_y=None,
                            height=dp(40), background_color=COLORS['primary'],
                            color=COLORS['white'])
        self._inputs[key] = sp_widget
        outer.add_widget(lbl)
        outer.add_widget(sp_widget)
        return outer

    def _save_plant(self, instance):
        name = ''
        if 'name' in self._inputs:
            w = self._inputs['name']
            name = w.text.strip() if hasattr(w, 'text') else w.text

        if not name:
            popup = Popup(
                title='خطا',
                content=Label(text='نام گیاه را وارد کنید!',
                              color=COLORS['error']),
                size_hint=(0.7, 0.25),
            )
            popup.open()
            return

        plant_data = {}
        for key, widget in self._inputs.items():
            if hasattr(widget, 'text'):
                plant_data[key] = widget.text.strip()

        plant_data.setdefault('suitable_for', 'خانه، آپارتمان')
        plant_data.setdefault('special_features', '')
        plant_data.setdefault('air', 'نرمال')
        plant_data['watering_days'] = 7
        plant_data['fertilizing_days'] = 30

        if self.app:
            self.app.add_custom_plant(plant_data)

        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        content.add_widget(Label(text='✅ گیاه با موفقیت اضافه شد!',
                                 font_size=sp(15), color=COLORS['primary'],
                                 halign='center'))
        ok_btn = Button(text='رفتن به لیست', size_hint_y=None, height=dp(44),
                        background_color=COLORS['primary'], color=COLORS['white'])
        content.add_widget(ok_btn)
        popup = Popup(title='موفقیت', content=content,
                      size_hint=(0.8, 0.3), auto_dismiss=False)
        ok_btn.bind(on_press=lambda x: (popup.dismiss(),
                                         self.app.go_to_screen('plant_list')))
        popup.open()
