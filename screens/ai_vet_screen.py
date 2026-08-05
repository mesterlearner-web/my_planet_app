"""
صفحه مشاوره گیاه‌پزشکی با هوش مصنوعی
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

import json
import threading
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.ui_components import COLORS, AdBanner, GreenButton

# مهم: کلید API هرگز نباید مستقیم داخل اپ باشد — هر کسی که فایل APK را
# داشته باشد می‌تواند آن را از داخل اپ استخراج کند. به‌جای آن، این صفحه به
# یک پراکسی امن و رایگان وصل می‌شود که کلید واقعی را روی سرور نگه می‌دارد.
# راهنمای کامل دیپلوی پراکسی: server/README.md
# بعد از دیپلوی، آدرس Worker خودتان را اینجا جایگزین کنید:
PROXY_URL = ""  # مثال: "https://plant-vet-proxy.YOUR-SUBDOMAIN.workers.dev"
# اختیاری: اگر در تنظیمات Worker مقدار APP_SHARED_SECRET را ست کردید،
# همان رشته را اینجا هم بگذارید تا فقط اپ خودتان بتواند از پراکسی استفاده کند
APP_SHARED_SECRET = ""


class AIVetScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.conversation = []
        self.selected_image_path = None
        self._chat_layout = None
        self._input_field = None
        self._send_btn = None
        self._status_lbl = None
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
        back_btn.bind(on_press=lambda x: self.app.go_to_screen('tools', 'right'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='🩺 مشاوره گیاه‌پزشکی', font_size=sp(18),
                                bold=True, color=COLORS['white'], halign='right'))

        # وضعیت اتصال
        status_text = ('🟢 آنلاین | هوش مصنوعی آماده مشاوره' if PROXY_URL
                       else '⚠️ نیاز به تنظیم پراکسی (server/README.md)')
        self._status_lbl = Label(
            text=status_text,
            font_size=sp(11), color=COLORS['text_secondary'],
            size_hint=(1, None), height=dp(26),
            halign='center',
        )
        status_bar = BoxLayout(size_hint=(1, None), height=dp(26),
                               padding=[dp(8), dp(2)])
        with status_bar.canvas.before:
            Color(*get_color_from_hex('#F9FBE7'))
            sbbg = Rectangle(pos=status_bar.pos, size=status_bar.size)
        status_bar.bind(pos=lambda i, v: setattr(sbbg, 'pos', v),
                        size=lambda i, v: setattr(sbbg, 'size', v))
        status_bar.add_widget(self._status_lbl)

        # چت
        chat_scroll = ScrollView(size_hint=(1, None), id='chat_scroll')
        self._chat_layout = BoxLayout(orientation='vertical', size_hint_y=None,
                                      spacing=dp(10), padding=[dp(10), dp(8)])
        self._chat_layout.bind(minimum_height=self._chat_layout.setter('height'))
        chat_scroll.add_widget(self._chat_layout)
        self._chat_scroll = chat_scroll

        # پیام خوش‌آمد
        self._add_bot_message(
            'سلام! من دستیار گیاه‌پزشکی هستم 🌿\n\n'
            'می‌توانید:\n'
            '• سوال‌های مراقبتی بپرسید\n'
            '• مشکل گیاه خود را توضیح دهید\n'
            '• عکس گیاه بیمار را بفرستید\n\n'
            'چطور می‌توانم کمک کنم؟'
        )

        # ناحیه ورودی
        input_area = BoxLayout(orientation='vertical', size_hint=(1, None),
                               height=dp(130), padding=[dp(8), dp(6)], spacing=dp(6))
        with input_area.canvas.before:
            Color(1, 1, 1, 1)
            iabg = Rectangle(pos=input_area.pos, size=input_area.size)
        input_area.bind(pos=lambda i, v: setattr(iabg, 'pos', v),
                        size=lambda i, v: setattr(iabg, 'size', v))

        # دکمه ارسال عکس
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                            height=dp(36), spacing=dp(8))
        img_btn = Button(
            text='📷 ارسال عکس',
            font_size=sp(12), size_hint=(None, 1), width=dp(120),
            background_normal='', background_color=get_color_from_hex('#E3F2FD'),
            color=get_color_from_hex('#1565C0'),
        )
        img_btn.bind(on_press=self._pick_image)

        self._img_status = Label(text='', font_size=sp(11),
                                 color=COLORS['text_secondary'])
        clear_btn = Button(
            text='پاک کردن', font_size=sp(11), size_hint=(None, 1), width=dp(80),
            background_normal='', background_color=get_color_from_hex('#FFEBEE'),
            color=get_color_from_hex('#C62828'),
        )
        clear_btn.bind(on_press=self._clear_chat)
        btn_row.add_widget(img_btn)
        btn_row.add_widget(self._img_status)
        btn_row.add_widget(clear_btn)

        # فیلد متن + ارسال
        text_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(60), spacing=dp(8))
        self._input_field = TextInput(
            hint_text='سوال یا مشکل گیاه خود را بنویسید...',
            font_size=sp(14), multiline=True,
            background_color=get_color_from_hex('#F1F8E9'),
            foreground_color=COLORS['text_dark'],
            hint_text_color=get_color_from_hex('#A5D6A7'),
        )
        self._send_btn = Button(
            text='📤', font_size=sp(24),
            size_hint=(None, 1), width=dp(56),
            background_normal='', background_color=COLORS['primary'],
            color=COLORS['white'],
        )
        self._send_btn.bind(on_press=self._send_message)

        text_row.add_widget(self._input_field)
        text_row.add_widget(self._send_btn)

        input_area.add_widget(btn_row)
        input_area.add_widget(text_row)

        # تبلیغ
        ad = AdBanner(size_hint=(None, None), size=(dp(300), dp(30)),
                      pos_hint={'center_x': 0.5})

        root.add_widget(chat_scroll)
        root.add_widget(header)
        root.add_widget(status_bar)
        root.add_widget(input_area)
        root.add_widget(ad)
        self.add_widget(root)

        def _fix(*a):
            status_bar.pos = (0, self.height - dp(60) - dp(26))
            chat_scroll.pos = (0, dp(130) + dp(30))
            chat_scroll.height = self.height - dp(60) - dp(26) - dp(130) - dp(30)
            input_area.pos = (0, dp(30))
            ad.pos = (self.width / 2 - dp(150), 0)
        Clock.schedule_once(_fix, 0.05)

    def _add_bot_message(self, text):
        msg_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            spacing=dp(8), padding=[dp(0), dp(4)])

        avatar = Label(text='🤖', font_size=sp(24), size_hint=(None, None),
                       size=(dp(36), dp(36)))

        bubble = BoxLayout(size_hint_y=None, padding=dp(12))
        with bubble.canvas.before:
            Color(*get_color_from_hex('#E8F5E9'))
            bbg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(12)])
        bubble.bind(pos=lambda i, v: setattr(bbg, 'pos', v),
                    size=lambda i, v: setattr(bbg, 'size', v))

        msg_lbl = Label(
            text=text, font_size=sp(13),
            color=COLORS['text_dark'],
            halign='right', valign='top',
            text_size=(self.width * 0.68, None),
        )
        msg_lbl.bind(texture_size=lambda i, v: setattr(msg_lbl, 'height', v[1] + dp(4)))

        bubble.add_widget(msg_lbl)
        bubble.bind(minimum_height=bubble.setter('height'))

        def _update_h(*a):
            bubble.height = msg_lbl.height + dp(24)
            msg_box.height = max(dp(52), bubble.height + dp(8))
        msg_lbl.bind(height=_update_h)
        Clock.schedule_once(lambda dt: _update_h(), 0.05)

        msg_box.add_widget(avatar)
        msg_box.add_widget(bubble)
        msg_box.add_widget(Widget())

        if self._chat_layout:
            self._chat_layout.add_widget(msg_box)
            Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _add_user_message(self, text, has_image=False):
        prefix = '📷 ' if has_image else ''
        msg_box = BoxLayout(orientation='horizontal', size_hint_y=None,
                            spacing=dp(8), padding=[dp(0), dp(4)])

        bubble = BoxLayout(size_hint_y=None, padding=dp(12))
        with bubble.canvas.before:
            Color(*COLORS['primary'])
            bbg = RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(12)])
        bubble.bind(pos=lambda i, v: setattr(bbg, 'pos', v),
                    size=lambda i, v: setattr(bbg, 'size', v))

        msg_lbl = Label(
            text=f'{prefix}{text}', font_size=sp(13),
            color=COLORS['white'],
            halign='right', valign='top',
            text_size=(self.width * 0.68, None),
        )
        msg_lbl.bind(texture_size=lambda i, v: setattr(msg_lbl, 'height', v[1] + dp(4)))

        bubble.add_widget(msg_lbl)

        def _update_h(*a):
            bubble.height = msg_lbl.height + dp(24)
            msg_box.height = max(dp(44), bubble.height + dp(8))
        msg_lbl.bind(height=_update_h)
        Clock.schedule_once(lambda dt: _update_h(), 0.05)

        msg_box.add_widget(Widget())
        msg_box.add_widget(bubble)
        msg_box.add_widget(Label(text='👤', font_size=sp(22),
                                  size_hint=(None, None), size=(dp(36), dp(36))))

        if self._chat_layout:
            self._chat_layout.add_widget(msg_box)
            Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _add_typing_indicator(self):
        typing = BoxLayout(orientation='horizontal', size_hint_y=None,
                           height=dp(44), spacing=dp(8), padding=[dp(4), dp(4)])
        typing.add_widget(Label(text='🤖', font_size=sp(22),
                                size_hint=(None, 1), width=dp(36)))
        dots_box = BoxLayout(size_hint_y=None, height=dp(36), padding=dp(8))
        with dots_box.canvas.before:
            Color(*get_color_from_hex('#E8F5E9'))
            dbbg = RoundedRectangle(pos=dots_box.pos, size=dots_box.size, radius=[dp(10)])
        dots_box.bind(pos=lambda i, v: setattr(dbbg, 'pos', v),
                      size=lambda i, v: setattr(dbbg, 'size', v))
        dots_box.add_widget(Label(text='در حال تایپ...', font_size=sp(12),
                                   color=COLORS['text_secondary']))
        typing.add_widget(dots_box)
        typing.add_widget(Widget())
        if self._chat_layout:
            self._chat_layout.add_widget(typing)
            self._typing_indicator = typing
            Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _remove_typing_indicator(self):
        if hasattr(self, '_typing_indicator') and self._typing_indicator:
            if self._chat_layout and self._typing_indicator in self._chat_layout.children:
                self._chat_layout.remove_widget(self._typing_indicator)
            self._typing_indicator = None

    def _send_message(self, instance):
        text = self._input_field.text.strip() if self._input_field else ''
        if not text:
            return

        has_image = self.selected_image_path is not None
        self._add_user_message(text, has_image=has_image)
        self._input_field.text = ''

        if self._send_btn:
            self._send_btn.disabled = True

        self._add_typing_indicator()

        # ارسال به API در thread جداگانه
        user_content = []
        if has_image:
            try:
                with open(self.selected_image_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                ext = os.path.splitext(self.selected_image_path)[1].lower()
                media_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                             '.png': 'image/png', '.gif': 'image/gif',
                             '.webp': 'image/webp'}
                media_type = media_map.get(ext, 'image/jpeg')
                user_content.append({
                    'type': 'image',
                    'source': {'type': 'base64', 'media_type': media_type, 'data': img_data}
                })
                self.selected_image_path = None
                if self._img_status:
                    self._img_status.text = ''
            except Exception as e:
                print(f'خطا در خواندن عکس: {e}')

        user_content.append({'type': 'text', 'text': text})
        self.conversation.append({'role': 'user', 'content': user_content})

        threading.Thread(target=self._call_api, daemon=True).start()

    def _call_api(self):
        if not PROXY_URL:
            msg = (
                'راه‌اندازی مشاوره هوش مصنوعی هنوز کامل نشده 🔧\n\n'
                'برای فعال شدن این بخش، یک پراکسی امن و رایگان دیپلوی '
                'کنید تا کلید API شما داخل اپ فاش نشود.\n'
                'راهنمای کامل: server/README.md'
            )
            Clock.schedule_once(lambda dt, m=msg: self._on_api_response(m), 0)
            return
        try:
            import urllib.request
            system_prompt = (
                'شما یک متخصص گیاه‌پزشکی و باغبانی حرفه‌ای هستید که به فارسی پاسخ می‌دهید. '
                'در مورد مشکلات گیاهان آپارتمانی، بیماری‌ها، آفات، شرایط رشد، '
                'آبیاری، کوددهی و هر موضوع مرتبط با گیاهان مشاوره تخصصی می‌دهید. '
                'پاسخ‌های خود را کوتاه، واضح و کاربردی بنویسید. '
                'از ایموجی‌های مناسب برای زیباتر کردن پاسخ استفاده کنید.'
            )
            payload = {
                'model': 'claude-sonnet-5',
                'max_tokens': 1024,
                'system': system_prompt,
                'messages': self.conversation,
            }
            data = json.dumps(payload).encode('utf-8')
            # توجه: هیچ کلید API از سمت اپ ارسال نمی‌شود؛ پراکسی خودش
            # کلید را (به‌صورت امن، سمت سرور) به درخواست اضافه می‌کند.
            headers = {'Content-Type': 'application/json'}
            if APP_SHARED_SECRET:
                headers['X-App-Secret'] = APP_SHARED_SECRET
            req = urllib.request.Request(
                PROXY_URL,
                data=data,
                headers=headers,
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                reply = result['content'][0]['text']
                self.conversation.append({'role': 'assistant', 'content': reply})
                Clock.schedule_once(lambda dt, r=reply: self._on_api_response(r), 0)
        except Exception as e:
            error_msg = f'❌ خطا در اتصال به سرور\nلطفاً اتصال اینترنت را بررسی کنید.\n\n{str(e)[:80]}'
            Clock.schedule_once(lambda dt, m=error_msg: self._on_api_response(m), 0)

    def _on_api_response(self, reply):
        self._remove_typing_indicator()
        self._add_bot_message(reply)
        if self._send_btn:
            self._send_btn.disabled = False

    def _pick_image(self, instance):
        """باز کردن file chooser برای انتخاب عکس"""
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.popup import Popup as KvPopup

        fc = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg', '*.webp'])
        popup = KvPopup(title='انتخاب عکس گیاه', content=fc,
                        size_hint=(0.95, 0.85))

        def _select(chooser, selection, touch):
            if selection:
                self.selected_image_path = selection[0]
                fname = os.path.basename(selection[0])
                if self._img_status:
                    self._img_status.text = f'✅ {fname[:20]}'
                popup.dismiss()

        fc.bind(on_submit=_select)
        popup.open()

    def _clear_chat(self, *args):
        self.conversation = []
        self.selected_image_path = None
        if self._img_status:
            self._img_status.text = ''
        if self._chat_layout:
            self._chat_layout.clear_widgets()
        self._add_bot_message('چت پاک شد. چطور می‌توانم کمک کنم؟ 🌱')

    def _scroll_to_bottom(self, *args):
        if self._chat_scroll:
            self._chat_scroll.scroll_y = 0
