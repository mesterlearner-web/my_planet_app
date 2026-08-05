"""
صفحه تایمر مراقبت - تا ۱۰۰ تایمر قابل نامگذاری
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.ui_components import COLORS, AdBanner, GreenButton, BottomNavBar
from utils.helpers import relative_time_fa


class TimerScreen(Screen):
    MAX_TIMERS = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.store = JsonStore('timers_data.json')
        self.timers = []
        self._list_layout = None
        self._load_timers()
        Clock.schedule_once(self._build_ui, 0)

    def _load_timers(self):
        try:
            if self.store.exists('timers'):
                self.timers = self.store.get('timers')['data']
        except Exception:
            self.timers = []

    def _save_timers(self):
        try:
            self.store.put('timers', data=self.timers)
        except Exception as e:
            print(f'خطا در ذخیره تایمر: {e}')

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
        back_btn.bind(on_press=lambda x: self.app.go_to_screen('tools', 'right'))

        header.add_widget(back_btn)
        header.add_widget(Label(text='⏰ تایمر مراقبت', font_size=sp(20),
                                bold=True, color=COLORS['white'], halign='right'))

        add_btn = Button(text='＋', font_size=sp(22), size_hint=(None, 1),
                         width=dp(44), background_normal='',
                         background_color=[0, 0, 0, 0], color=COLORS['white'])
        add_btn.bind(on_press=lambda x: self._show_add_popup())
        header.add_widget(add_btn)

        # اطلاعات تعداد
        info_bar = BoxLayout(size_hint=(1, None), height=dp(36),
                             padding=[dp(14), dp(4)])
        with info_bar.canvas.before:
            Color(*get_color_from_hex('#E8F5E9'))
            ibbg = Rectangle(pos=info_bar.pos, size=info_bar.size)
        info_bar.bind(pos=lambda i, v: setattr(ibbg, 'pos', v),
                      size=lambda i, v: setattr(ibbg, 'size', v))

        self._count_label = Label(
            text=f'تعداد تایمر: {len(self.timers)} / {self.MAX_TIMERS}',
            font_size=sp(12), color=COLORS['text_secondary'],
            halign='right',
        )
        self._count_label.bind(size=self._count_label.setter('text_size'))
        info_bar.add_widget(self._count_label)

        # لیست تایمرها
        scroll = ScrollView(size_hint=(1, None))
        self._list_layout = BoxLayout(orientation='vertical', size_hint_y=None,
                                      spacing=dp(8), padding=[dp(12), dp(10)])
        self._list_layout.bind(minimum_height=self._list_layout.setter('height'))
        scroll.add_widget(self._list_layout)

        # نوار پایین
        nav = BottomNavBar(app_ref=self.app, active_tab='tools')
        nav.pos_hint = {'x': 0, 'y': 0}
        ad = AdBanner(size_hint=(None, None), size=(dp(300), dp(30)),
                      pos_hint={'center_x': 0.5})

        root.add_widget(scroll)
        root.add_widget(header)
        root.add_widget(info_bar)
        root.add_widget(ad)
        root.add_widget(nav)
        self.add_widget(root)

        def _fix(*a):
            info_bar.pos = (0, self.height - dp(60) - dp(36))
            scroll.pos = (0, dp(60) + dp(30))
            scroll.height = self.height - dp(60) - dp(36) - dp(60) - dp(30)
            ad.pos = (self.width / 2 - dp(150), dp(60))
        Clock.schedule_once(_fix, 0.05)
        self._render_timers()

    def _render_timers(self):
        if not self._list_layout:
            return
        self._list_layout.clear_widgets()

        if not self.timers:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                  height=dp(200), padding=dp(30))
            empty_box.add_widget(Label(text='⏰', font_size=sp(60),
                                       color=COLORS['divider'], size_hint_y=None, height=dp(80)))
            empty_box.add_widget(Label(
                text='هنوز تایمری ندارید!\nدکمه ＋ را بزنید تا اولین تایمر را بسازید.',
                font_size=sp(14), color=COLORS['text_secondary'],
                halign='center',
            ))
            self._list_layout.add_widget(empty_box)
        else:
            for i, timer in enumerate(self.timers):
                card = self._make_timer_card(timer, i)
                self._list_layout.add_widget(card)

        if self._count_label:
            self._count_label.text = f'تعداد تایمر: {len(self.timers)} / {self.MAX_TIMERS}'

    def _make_timer_card(self, timer, idx):
        is_active = timer.get('active', True)
        bg_color = get_color_from_hex('#E8F5E9') if is_active else get_color_from_hex('#F5F5F5')
        title_color = COLORS['primary'] if is_active else get_color_from_hex('#9E9E9E')

        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(95),
                         padding=[dp(14), dp(10)], spacing=dp(6))
        with card.canvas.before:
            Color(*bg_color)
            cbg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(pos=lambda i, v: setattr(cbg, 'pos', v),
                  size=lambda i, v: setattr(cbg, 'size', v))

        # ردیف اول: نام + وضعیت
        row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        type_icons = {
            'آبیاری': '💧', 'کود دادن': '🌿', 'تعویض خاک': '🪴',
            'هرس': '✂️', 'سم‌پاشی': '💊', 'سایر': '📋',
        }
        timer_type = timer.get('timer_type', 'سایر')
        icon = type_icons.get(timer_type, '📋')

        name_lbl = Label(
            text=f'{icon} {timer.get("name", "بی‌نام")}',
            font_size=sp(15), bold=True, color=title_color,
            halign='right', valign='middle',
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))

        status_lbl = Label(
            text='✅ فعال' if is_active else '⏸ متوقف',
            font_size=sp(11),
            color=COLORS['primary'] if is_active else get_color_from_hex('#9E9E9E'),
            size_hint=(None, 1), width=dp(75),
        )
        row1.add_widget(name_lbl)
        row1.add_widget(status_lbl)

        # ردیف دوم: اطلاعات
        row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22),
                         spacing=dp(10))
        interval_days = timer.get('interval_days', 7)
        next_time = timer.get('next_time', '')
        if next_time:
            next_text = f'بعدی: {relative_time_fa(next_time)}'
        else:
            next_text = 'تنظیم نشده'

        info_lbl = Label(
            text=f'هر {interval_days} روز  |  {next_text}',
            font_size=sp(11), color=COLORS['text_secondary'],
            halign='right',
        )
        info_lbl.bind(size=info_lbl.setter('text_size'))
        row2.add_widget(info_lbl)

        # دکمه‌ها
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(28), spacing=dp(8))
        btn_row.add_widget(Widget())

        del_btn = Button(
            text='🗑 حذف', font_size=sp(11), size_hint=(None, 1), width=dp(70),
            background_normal='', background_color=get_color_from_hex('#FFEBEE'),
            color=get_color_from_hex('#C62828'),
        )
        _idx = idx
        del_btn.bind(on_press=lambda x, i=_idx: self._delete_timer(i))

        toggle_btn = Button(
            text='⏸ توقف' if is_active else '▶ فعال‌سازی',
            font_size=sp(11), size_hint=(None, 1), width=dp(90),
            background_normal='',
            background_color=get_color_from_hex('#E3F2FD'),
            color=get_color_from_hex('#1565C0'),
        )
        toggle_btn.bind(on_press=lambda x, i=_idx: self._toggle_timer(i))

        btn_row.add_widget(del_btn)
        btn_row.add_widget(toggle_btn)

        card.add_widget(row1)
        card.add_widget(row2)
        card.add_widget(btn_row)
        return card

    def _show_add_popup(self):
        if len(self.timers) >= self.MAX_TIMERS:
            self._show_message('محدودیت', f'حداکثر {self.MAX_TIMERS} تایمر می‌توانید داشته باشید.')
            return

        popup_content = BoxLayout(orientation='vertical', spacing=dp(14),
                                  padding=[dp(16), dp(16)])

        # نام تایمر
        popup_content.add_widget(Label(text='نام تایمر:', font_size=sp(14),
                                       color=COLORS['text_primary'],
                                       size_hint_y=None, height=dp(28),
                                       halign='right'))
        name_input = TextInput(
            hint_text='مثلاً: آبیاری مونسترا',
            font_size=sp(14), multiline=False,
            size_hint_y=None, height=dp(44),
            background_color=get_color_from_hex('#F1F8E9'),
            halign='right',
        )
        popup_content.add_widget(name_input)

        # نوع تایمر
        popup_content.add_widget(Label(text='نوع مراقبت:', font_size=sp(14),
                                       color=COLORS['text_primary'],
                                       size_hint_y=None, height=dp(28),
                                       halign='right'))
        type_spinner = Spinner(
            text='آبیاری',
            values=['آبیاری', 'کود دادن', 'تعویض خاک', 'هرس', 'سم‌پاشی', 'سایر'],
            size_hint_y=None, height=dp(44),
            background_color=COLORS['primary'],
            color=COLORS['white'],
        )
        popup_content.add_widget(type_spinner)

        # فاصله زمانی
        popup_content.add_widget(Label(text='هر چند روز یکبار:', font_size=sp(14),
                                       color=COLORS['text_primary'],
                                       size_hint_y=None, height=dp(28),
                                       halign='right'))
        interval_spinner = Spinner(
            text='7',
            values=['1', '2', '3', '5', '7', '10', '14', '21', '30', '45', '60', '90'],
            size_hint_y=None, height=dp(44),
            background_color=get_color_from_hex('#00796B'),
            color=COLORS['white'],
        )
        popup_content.add_widget(interval_spinner)

        # دکمه‌ها
        btn_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                            size_hint_y=None, height=dp(48))
        cancel_btn = Button(text='انصراف', font_size=sp(14),
                            background_color=get_color_from_hex('#BDBDBD'),
                            color=COLORS['white'])
        save_btn = Button(text='ذخیره ⏰', font_size=sp(14),
                          background_color=COLORS['primary'],
                          color=COLORS['white'])
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        popup_content.add_widget(btn_row)

        popup = Popup(
            title='افزودن تایمر جدید',
            content=popup_content,
            size_hint=(0.9, 0.72),
            auto_dismiss=False,
        )

        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        save_btn.bind(on_press=lambda x: self._save_new_timer(
            popup, name_input.text, type_spinner.text, int(interval_spinner.text)
        ))
        popup.open()

    def _save_new_timer(self, popup, name, timer_type, interval_days):
        if not name.strip():
            return
        next_time = (datetime.now() + timedelta(days=interval_days)).isoformat()
        new_timer = {
            'id': len(self.timers) + 1,
            'name': name.strip(),
            'timer_type': timer_type,
            'interval_days': interval_days,
            'next_time': next_time,
            'active': True,
            'created': datetime.now().isoformat(),
        }
        self.timers.append(new_timer)
        self._save_timers()
        popup.dismiss()
        self._render_timers()

    def _delete_timer(self, idx):
        def _confirm(popup):
            if 0 <= idx < len(self.timers):
                self.timers.pop(idx)
                self._save_timers()
                self._render_timers()
            popup.dismiss()

        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        content.add_widget(Label(text='آیا مطمئن هستید؟', font_size=sp(15),
                                 color=COLORS['text_dark']))
        btn_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                            size_hint_y=None, height=dp(44))
        no_btn = Button(text='خیر', background_color=get_color_from_hex('#BDBDBD'),
                        color=COLORS['white'])
        yes_btn = Button(text='بله، حذف شود', background_color=COLORS['error'],
                         color=COLORS['white'])
        btn_row.add_widget(no_btn)
        btn_row.add_widget(yes_btn)
        content.add_widget(btn_row)

        popup = Popup(title='حذف تایمر', content=content,
                      size_hint=(0.8, 0.3), auto_dismiss=False)
        no_btn.bind(on_press=lambda x: popup.dismiss())
        yes_btn.bind(on_press=lambda x: _confirm(popup))
        popup.open()

    def _toggle_timer(self, idx):
        if 0 <= idx < len(self.timers):
            self.timers[idx]['active'] = not self.timers[idx].get('active', True)
            self._save_timers()
            self._render_timers()

    def _show_message(self, title, msg):
        content = BoxLayout(orientation='vertical', padding=dp(16))
        content.add_widget(Label(text=msg, font_size=sp(14),
                                 color=COLORS['text_dark'], halign='center'))
        ok_btn = Button(text='باشه', size_hint_y=None, height=dp(44),
                        background_color=COLORS['primary'], color=COLORS['white'])
        content.add_widget(ok_btn)
        popup = Popup(title=title, content=content,
                      size_hint=(0.8, 0.3), auto_dismiss=True)
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def on_enter(self):
        self._load_timers()
        self._render_timers()
