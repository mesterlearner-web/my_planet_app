"""
صفحه جزئیات گیاه
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.ui_components import (COLORS, PLANT_CATEGORY_COLORS, AdBanner,
                                       PlantImage, InfoRow, SectionTitle, GreenButton,
                                       get_plant_image)


class PlantDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.plant = None

    def load_plant(self, plant_data):
        self.plant = plant_data
        self.clear_widgets()
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, dt):
        if not self.plant:
            return
        p = self.plant

        root = FloatLayout()
        with root.canvas.before:
            Color(*COLORS['background'])
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                  size=lambda i, v: setattr(bg, 'size', v))

        # --- هدر رنگی ---
        cat_color = PLANT_CATEGORY_COLORS.get(p.get('category', ''), COLORS['primary'])
        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(258),
                           pos_hint={'top': 1})
        with header.canvas.before:
            Color(*cat_color)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', v),
                    size=lambda i, v: setattr(hbg, 'size', v))

        # نوار بالا
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(56), padding=[dp(10), dp(8)])
        back_btn = Button(text='←', font_size=sp(22), size_hint=(None, 1),
                          width=dp(44), background_normal='',
                          background_color=[0, 0, 0, 0], color=COLORS['white'])
        back_btn.bind(on_press=lambda x: self.app.go_to_screen('plant_list', 'right'))

        name_lbl = Label(text=p.get('name', ''), font_size=sp(19), bold=True,
                         color=COLORS['white'], halign='right')
        top_bar.add_widget(back_btn)
        top_bar.add_widget(name_lbl)

        # اطلاعات سریع زیر هدر
        quick_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                              height=dp(50), padding=[dp(16), dp(4)], spacing=dp(8))
        quick_items = [
            ('💧', p.get('watering', '-')),
            ('☀️', p.get('light', '-')),
            ('⭐', p.get('care_level', '-')),
        ]
        for icon, val in quick_items:
            qb = BoxLayout(orientation='vertical', spacing=dp(2))
            qb.add_widget(Label(text=icon, font_size=sp(18), color=COLORS['white'],
                                size_hint_y=None, height=dp(22)))
            qb.add_widget(Label(text=val, font_size=sp(10),
                                color=get_color_from_hex('#E8F5E9'),
                                size_hint_y=None, height=dp(20), halign='center'))
            quick_row.add_widget(qb)

        # عکس بزرگ گیاه (دایره‌ای)
        img_row = BoxLayout(size_hint_y=None, height=dp(138),
                            padding=[0, dp(4)])
        plant_img = PlantImage(
            plant_name=p.get('name', ''),
            category=p.get('category', 'آپارتمانی'),
            image_path=get_plant_image(p.get('image', '')),
            corner_radius=dp(65),
            size_hint=(None, None), size=(dp(130), dp(130)),
            pos_hint={'center_x': 0.5},
        )
        img_row.add_widget(Widget())
        img_row.add_widget(plant_img)
        img_row.add_widget(Widget())

        sci_lbl = Label(text=p.get('scientific_name', ''), font_size=sp(12),
                        italic=True, color=get_color_from_hex('#C8E6C9'),
                        size_hint_y=None, height=dp(20))
        header.add_widget(top_bar)
        header.add_widget(img_row)
        header.add_widget(sci_lbl)
        header.add_widget(quick_row)

        # --- محتوا ---
        scroll = ScrollView(size_hint=(1, None))
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=dp(10), padding=[dp(12), dp(10)])
        content.bind(minimum_height=content.setter('height'))

        # توضیحات
        content.add_widget(self._make_section(
            '📋 معرفی گیاه',
            p.get('description', 'اطلاعاتی موجود نیست.'),
        ))

        # مشخصات
        content.add_widget(SectionTitle(text='📊 مشخصات کامل'))
        specs_card = self._make_card()
        specs_inner = BoxLayout(orientation='vertical')
        rows = [
            ('نیاز به نور', p.get('light', '-')),
            ('نیاز به آبیاری', p.get('watering', '-')),
            ('بهترین هوا', p.get('air', '-')),
            ('قیمت', p.get('price_range', '-')),
            ('میزان نگهداری', p.get('care_level', '-')),
            ('مناسب برای', p.get('suitable_for', '-')),
            ('ویژگی خاص', p.get('special_features', '-')),
            ('دسته‌بندی', p.get('category', '-')),
        ]
        for k, v in rows:
            row = InfoRow(k, v)
            specs_inner.add_widget(row)
            div = Widget(size_hint_y=None, height=dp(1))
            with div.canvas:
                Color(*COLORS['divider'])
                Rectangle(pos=div.pos, size=div.size)
            div.bind(pos=lambda i, v2: None, size=lambda i, v2: None)
            specs_inner.add_widget(div)
        specs_card.add_widget(specs_inner)
        content.add_widget(specs_card)

        # شرایط رشد
        content.add_widget(self._make_section(
            '🌱 شرایط رشد مناسب',
            p.get('growth_conditions', 'اطلاعاتی موجود نیست.'),
            color=get_color_from_hex('#E3F2FD'),
        ))

        # مشکلات رایج
        content.add_widget(self._make_section(
            '⚠️ مشکلات شایع',
            p.get('common_problems', 'اطلاعاتی موجود نیست.'),
            color=get_color_from_hex('#FFF8E1'),
        ))

        # روش درمان
        content.add_widget(self._make_section(
            '💊 روش درمان',
            p.get('treatment', 'اطلاعاتی موجود نیست.'),
            color=get_color_from_hex('#F3E5F5'),
        ))

        # دکمه‌های عمل
        btns = BoxLayout(orientation='horizontal', size_hint_y=None,
                         height=dp(50), spacing=dp(10))

        timer_btn = GreenButton(text='⏰ تنظیم یادآور')
        timer_btn.bind(on_press=lambda x: self.app.go_to_screen('timers'))

        vet_btn = Button(
            text='🩺 مشاوره گیاه‌پزشکی',
            size_hint_y=None, height=dp(50),
            background_normal='', background_color=[0, 0, 0, 0],
            color=COLORS['primary'], font_size=sp(14), bold=True,
        )
        with vet_btn.canvas.before:
            Color(*COLORS['primary'])
            Line(rounded_rectangle=(0, 0, 1, 1, dp(12)), width=dp(1.5))

        def _draw_vet(btn, *a):
            btn.canvas.before.clear()
            with btn.canvas.before:
                Color(*COLORS['primary'])
                Line(rounded_rectangle=(btn.x, btn.y, btn.width, btn.height, dp(12)), width=dp(1.5))
        vet_btn.bind(pos=_draw_vet, size=_draw_vet)
        vet_btn.bind(on_press=lambda x: self.app.go_to_screen('ai_vet'))

        btns.add_widget(timer_btn)
        btns.add_widget(vet_btn)
        content.add_widget(btns)
        content.add_widget(Widget(size_hint_y=None, height=dp(16)))

        scroll.add_widget(content)

        # تبلیغ
        ad = AdBanner(size_hint=(None, None), size=(dp(300), dp(30)),
                      pos_hint={'center_x': 0.5})

        root.add_widget(scroll)
        root.add_widget(header)
        root.add_widget(ad)
        self.add_widget(root)

        def _fix(*a):
            scroll.pos = (0, dp(30))
            scroll.height = self.height - dp(258) - dp(30)
            ad.pos = (self.width / 2 - dp(150), 0)
        Clock.schedule_once(_fix, 0.05)

    def _make_card(self, bg_color=None):
        if bg_color is None:
            bg_color = COLORS['card']
        card = FloatLayout(size_hint_y=None)
        with card.canvas.before:
            Color(*bg_color)
            bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                  size=lambda i, v: setattr(bg, 'size', v))
        return card

    def _make_section(self, title, body_text, color=None):
        if color is None:
            color = COLORS['card']
        outer = BoxLayout(orientation='vertical', size_hint_y=None,
                          spacing=dp(0))

        title_lbl = Label(text=title, font_size=sp(15), bold=True,
                          color=COLORS['text_primary'], size_hint_y=None,
                          height=dp(36), halign='right')
        title_lbl.bind(size=title_lbl.setter('text_size'))
        outer.add_widget(title_lbl)

        body = Label(
            text=body_text,
            font_size=sp(13),
            color=COLORS['text_dark'],
            halign='right',
            valign='top',
            size_hint_y=None,
            text_size=(self.width - dp(32), None),
        )
        body.bind(texture_size=lambda i, v: setattr(body, 'height', v[1] + dp(16)))

        card = BoxLayout(size_hint_y=None, padding=dp(12))
        with card.canvas.before:
            Color(*color)
            cbg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda i, v: setattr(cbg, 'pos', v),
                  size=lambda i, v: setattr(cbg, 'size', v))
        card.add_widget(body)
        outer.add_widget(card)

        def _update_heights(*a):
            card.height = body.height + dp(24)
            outer.height = title_lbl.height + card.height + dp(4)
        body.bind(height=lambda i, v: _update_heights())
        Clock.schedule_once(lambda dt: _update_heights(), 0.1)

        return outer
