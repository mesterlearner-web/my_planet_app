"""
صفحه ابزار مراقبت
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.ui_components import COLORS, AdBanner, SectionTitle, BottomNavBar


class ToolsScreen(Screen):
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
        back_btn.bind(on_press=lambda x: self.app.go_to_screen('home', 'right'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='🔧 ابزار مراقبت', font_size=sp(20),
                                bold=True, color=COLORS['white'], halign='right'))

        # محتوا
        scroll = ScrollView(size_hint=(1, None))
        content = BoxLayout(orientation='vertical', size_hint_y=None,
                            spacing=dp(14), padding=[dp(14), dp(14)])
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(SectionTitle(text='ابزارهای در دسترس'))

        tools = [
            {
                'icon': '⏰',
                'title': 'تایمر مراقبت',
                'desc': 'تا ۱۰۰ تایمر برای آبیاری، کود، تعویض خاک و...',
                'screen': 'timers',
                'color': get_color_from_hex('#1565C0'),
                'bg': get_color_from_hex('#E3F2FD'),
            },
            {
                'icon': '🩺',
                'title': 'مشاوره گیاه‌پزشکی',
                'desc': 'با ارسال عکس و توضیح، از هوش مصنوعی مشاوره بگیرید',
                'screen': 'ai_vet',
                'color': get_color_from_hex('#2E7D32'),
                'bg': get_color_from_hex('#E8F5E9'),
            },
            {
                'icon': '📋',
                'title': 'لیست گیاهان',
                'desc': 'مشاهده اطلاعات کامل تمام گیاهان',
                'screen': 'plant_list',
                'color': get_color_from_hex('#6A1B9A'),
                'bg': get_color_from_hex('#F3E5F5'),
            },
            {
                'icon': '➕',
                'title': 'افزودن گیاه جدید',
                'desc': 'گیاهان سفارشی خود را اضافه کنید',
                'screen': 'add_plant',
                'color': get_color_from_hex('#E65100'),
                'bg': get_color_from_hex('#FFF3E0'),
            },
        ]

        for t in tools:
            card = self._make_tool_card(t)
            content.add_widget(card)

        # راهنما
        content.add_widget(SectionTitle(text='راهنمای سریع 💡'))
        tips = [
            ('💧', 'آبیاری منظم', 'اکثر گیاهان آپارتمانی به آبیاری هر ۷-۱۰ روز یکبار نیاز دارند.'),
            ('☀️', 'نور مناسب', 'گیاهان را از نور مستقیم تابستان دور نگه دارید.'),
            ('🌡️', 'دما', 'دمای ایده‌آل برای اکثر گیاهان ۱۸ تا ۲۸ درجه است.'),
            ('💦', 'رطوبت', 'گیاهان استوایی به رطوبت بالاتری نیاز دارند.'),
            ('🌱', 'خاک', 'هر ۲-۳ سال یکبار خاک و گلدان را عوض کنید.'),
        ]
        for icon, title, tip in tips:
            tip_card = self._make_tip_card(icon, title, tip)
            content.add_widget(tip_card)

        content.add_widget(Widget(size_hint_y=None, height=dp(10)))
        scroll.add_widget(content)

        # nav
        nav = BottomNavBar(app_ref=self.app, active_tab='tools')
        nav.pos_hint = {'x': 0, 'y': 0}
        ad = AdBanner(size_hint=(None, None), size=(dp(300), dp(30)),
                      pos_hint={'center_x': 0.5})

        root.add_widget(scroll)
        root.add_widget(header)
        root.add_widget(ad)
        root.add_widget(nav)
        self.add_widget(root)

        def _fix(*a):
            scroll.pos = (0, dp(60) + dp(30))
            scroll.height = self.height - dp(60) - dp(60) - dp(30)
            ad.pos = (self.width / 2 - dp(150), dp(60))
        Clock.schedule_once(_fix, 0.05)

    def _make_tool_card(self, tool_data):
        card = Button(
            background_normal='', background_color=[0, 0, 0, 0],
            size_hint_y=None, height=dp(90),
        )
        with card.canvas.before:
            Color(*tool_data['bg'])
            cbg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda i, v: setattr(cbg, 'pos', v),
                  size=lambda i, v: setattr(cbg, 'size', v))

        inner = BoxLayout(orientation='horizontal', spacing=dp(14),
                          padding=[dp(14), dp(10)],
                          pos=card.pos, size=card.size)
        card.bind(pos=lambda i, v: setattr(inner, 'pos', v),
                  size=lambda i, v: setattr(inner, 'size', v))

        icon_lbl = Label(text=tool_data['icon'], font_size=sp(40),
                         size_hint=(None, 1), width=dp(55))

        text_col = BoxLayout(orientation='vertical', spacing=dp(4))
        title_lbl = Label(text=tool_data['title'], font_size=sp(16), bold=True,
                          color=tool_data['color'], halign='right', valign='middle',
                          size_hint_y=None, height=dp(30))
        title_lbl.bind(size=title_lbl.setter('text_size'))

        desc_lbl = Label(text=tool_data['desc'], font_size=sp(12),
                         color=COLORS['text_secondary'], halign='right',
                         valign='top')
        desc_lbl.bind(size=desc_lbl.setter('text_size'))

        text_col.add_widget(title_lbl)
        text_col.add_widget(desc_lbl)

        arrow = Label(text='›', font_size=sp(26), color=tool_data['color'],
                      size_hint=(None, 1), width=dp(20))

        inner.add_widget(icon_lbl)
        inner.add_widget(text_col)
        inner.add_widget(arrow)
        card.add_widget(inner)

        _scr = tool_data['screen']
        card.bind(on_press=lambda x, s=_scr: self.app.go_to_screen(s))
        return card

    def _make_tip_card(self, icon, title, tip):
        outer = BoxLayout(orientation='horizontal', size_hint_y=None,
                          height=dp(70), spacing=dp(12), padding=[dp(12), dp(8)])
        with outer.canvas.before:
            Color(1, 1, 1, 1)
            bg = RoundedRectangle(pos=outer.pos, size=outer.size, radius=[dp(10)])
        outer.bind(pos=lambda i, v: setattr(bg, 'pos', v),
                   size=lambda i, v: setattr(bg, 'size', v))

        outer.add_widget(Label(text=icon, font_size=sp(28), size_hint=(None, 1),
                               width=dp(40)))
        inner = BoxLayout(orientation='vertical', spacing=dp(2))
        inner.add_widget(Label(text=title, font_size=sp(13), bold=True,
                               color=COLORS['text_primary'], halign='right',
                               size_hint_y=None, height=dp(24)))
        desc = Label(text=tip, font_size=sp(11), color=COLORS['text_secondary'],
                     halign='right', valign='top')
        desc.bind(size=desc.setter('text_size'))
        inner.add_widget(desc)
        outer.add_widget(inner)
        return outer


