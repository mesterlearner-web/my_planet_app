"""
صفحه اصلی برنامه
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
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
                                       PlantCard, SectionTitle, GreenButton, BottomNavBar)
from data.plants_db import PLANTS_DATA
from kivy.storage.jsonstore import JsonStore


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        # مقداردهی اولیه قبل از build - چون main.py بلافاصله بعد از ساخت
        # صفحات current='home' را ست می‌کند و همین باعث فراخوانی سریع
        # on_enter می‌شود، حتی پیش از اجرای _build_ui (که با تأخیر یک
        # فریم زمان‌بندی شده). بدون این خط، همان اولین اجرا با خطای
        # AttributeError متوقف می‌شد.
        self._timer_count_lbl = None
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, dt):
        root = FloatLayout()

        with root.canvas.before:
            Color(*COLORS['background'])
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda i, v: setattr(self._bg, 'pos', v),
                  size=lambda i, v: setattr(self._bg, 'size', v))

        # --- نوار بالا ---
        header = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(130),
            pos_hint={'top': 1},
        )
        with header.canvas.before:
            Color(*COLORS['primary'])
            self._hdr_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(self._hdr_bg, 'pos', v),
                    size=lambda i, v: setattr(self._hdr_bg, 'size', v))

        # سطر اول: عنوان + آیکون جستجو
        top_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(60), padding=[dp(16), dp(8)])
        search_btn = Button(text='🔍', font_size=sp(22), size_hint=(None, 1),
                            width=dp(44), background_normal='',
                            background_color=[0, 0, 0, 0], color=COLORS['white'])
        search_btn.bind(on_press=lambda x: self.app.go_to_screen('search'))

        title_lbl = Label(text='🌿 گیاهیار', font_size=sp(24), bold=True,
                          color=COLORS['white'], halign='right')
        add_btn = Button(text='＋', font_size=sp(24), size_hint=(None, 1),
                         width=dp(44), background_normal='',
                         background_color=[0, 0, 0, 0], color=COLORS['white'])
        add_btn.bind(on_press=lambda x: self.app.go_to_screen('add_plant'))

        top_row.add_widget(search_btn)
        top_row.add_widget(title_lbl)
        top_row.add_widget(add_btn)

        # سطر دوم: خوش‌آمد
        welcome_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                                height=dp(30), padding=[dp(16), 0])
        welcome_lbl = Label(
            text='مراقبت هوشمند از گیاهان خانگی شما 🌱',
            font_size=sp(13), color=get_color_from_hex('#C8E6C9'),
            halign='right',
        )
        welcome_lbl.bind(size=welcome_lbl.setter('text_size'))
        welcome_row.add_widget(welcome_lbl)

        # آمار کوچک
        stats_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                              height=dp(40), padding=[dp(12), dp(4)], spacing=dp(8))
        total = len(self.app.all_plants) if self.app else len(PLANTS_DATA)
        self._timer_count_lbl = None
        for icon, num, lbl in [('🌿', total, 'گیاه'), ('📂', 4, 'دسته'),
                                ('⏰', self._get_timer_count(), 'تایمر')]:
            stat_box = BoxLayout(orientation='horizontal', spacing=dp(4))
            stat_box.add_widget(Label(text=icon, font_size=sp(14)))
            num_lbl = Label(text=f'{num} {lbl}', font_size=sp(12),
                            color=get_color_from_hex('#E8F5E9'))
            if lbl == 'تایمر':
                self._timer_count_lbl = num_lbl
            stat_box.add_widget(num_lbl)
            stats_row.add_widget(stat_box)

        header.add_widget(top_row)
        header.add_widget(welcome_row)
        header.add_widget(stats_row)

        # --- محتوای اصلی قابل اسکرول ---
        scroll = ScrollView(
            size_hint=(1, None),
            pos_hint={'x': 0},
        )
        root.bind(height=lambda i, v: setattr(scroll, 'height', v - dp(130) - dp(60) - dp(30)))
        root.bind(height=lambda i, v: scroll.setter('y')(scroll, dp(60) + dp(30)))

        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=dp(8), padding=[dp(12), dp(12)])
        content.bind(minimum_height=content.setter('height'))

        # --- دکمه‌های اصلی ---
        content.add_widget(SectionTitle(text='امکانات برنامه'))

        menu_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(220))
        menu_items = [
            ('🌿', 'لیست گیاهان', 'plant_list', COLORS['primary']),
            ('🔧', 'ابزار مراقبت', 'tools', get_color_from_hex('#00796B')),
            ('🛒', 'فروشگاه', 'shop', get_color_from_hex('#E65100')),
            ('🔍', 'جستجو', 'search', get_color_from_hex('#6A1B9A')),
        ]
        for icon, label, screen, color in menu_items:
            btn = self._make_menu_btn(icon, label, screen, color)
            menu_grid.add_widget(btn)
        content.add_widget(menu_grid)

        # --- گیاهان پیشنهادی ---
        content.add_widget(SectionTitle(text='گیاهان پیشنهادی 🌟'))
        for plant in PLANTS_DATA[:6]:
            card = PlantCard(plant_data=plant, app_ref=self.app,
                             size_hint_y=None, height=dp(100))
            content.add_widget(card)
            content.add_widget(Widget(size_hint_y=None, height=dp(4)))

        see_all_btn = GreenButton(text='مشاهده همه گیاهان ←')
        see_all_btn.bind(on_press=lambda x: self.app.go_to_screen('plant_list'))
        content.add_widget(see_all_btn)
        content.add_widget(Widget(size_hint_y=None, height=dp(10)))

        scroll.add_widget(content)

        # --- نوار تبلیغاتی (وسط پایین) ---
        ad_container = BoxLayout(
            size_hint=(None, None),
            size=(dp(300), dp(30)),
            pos_hint={'center_x': 0.5},
        )
        root.bind(height=lambda i, v: setattr(ad_container, 'y', dp(60)))
        ad_container.add_widget(AdBanner())

        # --- نوار ناوبری پایین ---
        nav = BottomNavBar(app_ref=self.app, active_tab='home')
        nav.pos_hint = {'x': 0, 'y': 0}

        root.add_widget(scroll)
        root.add_widget(header)
        root.add_widget(ad_container)
        root.add_widget(nav)

        self.add_widget(root)

        # تنظیم موقعیت اسکرول
        def _fix_scroll_pos(*a):
            scroll.pos = (0, dp(60) + dp(30))
            scroll.height = self.height - dp(130) - dp(60) - dp(30)
        Clock.schedule_once(_fix_scroll_pos, 0.05)

    def _make_menu_btn(self, icon, label, screen_name, color):
        btn = Button(
            background_normal='',
            background_color=[0, 0, 0, 0],
            size_hint_y=None,
            height=dp(100),
        )
        with btn.canvas.before:
            Color(*color[:3], 1)
            menu_bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(14)])
        btn.bind(
            pos=lambda i, v, r=menu_bg: setattr(r, 'pos', v),
            size=lambda i, v, r=menu_bg: setattr(r, 'size', v),
        )
        inner = BoxLayout(orientation='vertical', spacing=dp(4),
                          pos=btn.pos, size=btn.size, padding=dp(8))
        btn.bind(pos=lambda i, v: setattr(inner, 'pos', v),
                 size=lambda i, v: setattr(inner, 'size', v))
        inner.add_widget(Label(text=icon, font_size=sp(36), color=COLORS['white']))
        inner.add_widget(Label(text=label, font_size=sp(14), bold=True,
                               color=COLORS['white']))
        btn.add_widget(inner)

        _screen = screen_name
        _color = list(color)
        _dark = [max(0, c - 0.15) for c in _color[:3]] + [1]
        btn.bind(on_press=lambda x: self.app.go_to_screen(_screen))
        return btn

    def _get_timer_count(self):
        """تعداد تایمرهای ذخیره‌شده را می‌خواند (بدون وابستگی به یک JsonStore دیگر
        تا از ناهماهنگی داده جلوگیری شود)."""
        try:
            store = JsonStore('timers_data.json')
            if store.exists('timers'):
                return len(store.get('timers')['data'])
        except Exception:
            pass
        return 0

    def on_enter(self):
        # هر بار که کاربر به صفحه خانه برمی‌گردد، آمار را به‌روز کن
        if self._timer_count_lbl:
            self._timer_count_lbl.text = f'{self._get_timer_count()} تایمر'
