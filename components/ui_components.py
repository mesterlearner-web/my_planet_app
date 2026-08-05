"""
کامپوننت‌های مشترک UI
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.animation import Animation
import os

# رنگ‌های مشترک
COLORS = {
    'primary': get_color_from_hex('#2E7D32'),
    'primary_light': get_color_from_hex('#4CAF50'),
    'primary_dark': get_color_from_hex('#1B5E20'),
    'secondary': get_color_from_hex('#8BC34A'),
    'accent': get_color_from_hex('#FF6F00'),
    'background': get_color_from_hex('#F1F8E9'),
    'card': get_color_from_hex('#FFFFFF'),
    'text_primary': get_color_from_hex('#1B5E20'),
    'text_secondary': get_color_from_hex('#558B2F'),
    'text_dark': get_color_from_hex('#212121'),
    'divider': get_color_from_hex('#C8E6C9'),
    'warning': get_color_from_hex('#F9A825'),
    'error': get_color_from_hex('#C62828'),
    'white': get_color_from_hex('#FFFFFF'),
    'ad_bg': get_color_from_hex('#FFF9C4'),
    'shadow': get_color_from_hex('#00000020'),
}

PLANT_CATEGORY_COLORS = {
    'آپارتمانی': get_color_from_hex('#4CAF50'),
    'گلدار': get_color_from_hex('#E91E63'),
    'دارویی': get_color_from_hex('#009688'),
    'درخت میوه': get_color_from_hex('#FF9800'),
}

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')


def get_plant_image(image_filename):
    """پیدا کردن مسیر تصویر واقعی گیاه؛ اگر پیدا نشد None برمی‌گرداند
    تا فراخوان بتواند آیکون رنگی پیش‌فرض را نمایش دهد."""
    if not image_filename:
        return None
    path = os.path.join(IMAGES_DIR, image_filename)
    if os.path.exists(path):
        return path
    return None


class RoundedCard(FloatLayout):
    """کارت با گوشه‌های گرد"""
    radius = NumericProperty(dp(16))
    bg_color = ListProperty([1, 1, 1, 1])
    elevation = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas,
                  bg_color=self._update_canvas)
        from kivy.clock import Clock
        Clock.schedule_once(self._update_canvas, 0)
    
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # سایه
            Color(0, 0, 0, 0.1)
            RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[self.radius]
            )
            # پس‌زمینه
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )


class GreenButton(Button):
    """دکمه سبز استایل‌دار"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['primary']
        self.color = COLORS['white']
        self.font_size = sp(16)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(50)
        self.bind(pos=self._update_shape, size=self._update_shape)
    
    def _update_shape(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
    
    def on_press(self):
        anim = Animation(background_color=COLORS['primary_dark'], duration=0.1)
        anim.start(self)
    
    def on_release(self):
        anim = Animation(background_color=COLORS['primary'], duration=0.1)
        anim.start(self)


class OutlineButton(Button):
    """دکمه با حاشیه"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [0, 0, 0, 0]
        self.color = COLORS['primary']
        self.font_size = sp(14)
        self.size_hint_y = None
        self.height = dp(42)
        self.bind(pos=self._update_shape, size=self._update_shape)
    
    def _update_shape(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*COLORS['primary'])
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=dp(1.5))


class TopBar(BoxLayout):
    """نوار بالای صفحه"""
    title = StringProperty('')
    show_back = BooleanProperty(True)
    
    def __init__(self, app_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        
        with self.canvas.before:
            Color(*COLORS['primary'])
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _build(self):
        if self.show_back:
            back_btn = Button(
                text='←',
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=COLORS['white'],
                font_size=sp(22),
                bold=True,
            )
            back_btn.bind(on_press=self._go_back)
            self.add_widget(back_btn)
        
        title_label = Label(
            text=self.title,
            color=COLORS['white'],
            font_size=sp(20),
            bold=True,
            halign='center',
        )
        self.add_widget(title_label)
    
    def _go_back(self, instance):
        if self.app_ref:
            self.app_ref.go_back()


class AdBanner(BoxLayout):
    """بنر تبلیغاتی کوچک"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(30)  # ۱ سانت × تقریبی
        self.padding = [dp(5), dp(3)]
        self.spacing = dp(5)
        
        with self.canvas.before:
            Color(*COLORS['ad_bg'])
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # محتوای تبلیغ
        ad_icon = Label(text='📢', font_size=sp(12), size_hint=(None, 1), width=dp(20))
        ad_text = Label(
            text='تبلیغات - اینجا جای تبلیغ شماست',
            font_size=sp(10),
            color=get_color_from_hex('#795548'),
            halign='center',
        )
        ad_small = Label(
            text='Ads',
            font_size=sp(8),
            color=get_color_from_hex('#BDBDBD'),
            size_hint=(None, 1),
            width=dp(25),
        )
        
        self.add_widget(ad_icon)
        self.add_widget(ad_text)
        self.add_widget(ad_small)
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class PlantCard(Button):
    """کارت گیاه برای لیست"""
    
    def __init__(self, plant_data, app_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.plant_data = plant_data
        self.app_ref = app_ref
        self.background_normal = ''
        self.background_color = [0, 0, 0, 0]
        self.size_hint_y = None
        self.height = dp(100)
        
        with self.canvas.before:
            Color(*COLORS['card'])
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(0, 0, 0, 0.05)
            self._shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        
        self._build_content()
        self.bind(on_press=self._on_click)
    
    def _update_canvas(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._shadow.pos = (self.x + dp(2), self.y - dp(2))
        self._shadow.size = self.size
    
    def _build_content(self):
        content = BoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            padding=[dp(12), dp(8)],
            size=self.size,
            pos=self.pos,
        )
        self.bind(pos=lambda i, v: setattr(content, 'pos', v),
                  size=lambda i, v: setattr(content, 'size', v))
        
        # تصویر گیاه
        img_container = BoxLayout(
            size_hint=(None, 1),
            width=dp(82),
        )
        plant_image = PlantImage(
            plant_name=self.plant_data.get('name', ''),
            category=self.plant_data.get('category', 'آپارتمانی'),
            image_path=get_plant_image(self.plant_data.get('image', '')),
            size_hint=(1, 1),
        )
        img_container.add_widget(plant_image)
        
        # اطلاعات گیاه
        info_layout = BoxLayout(orientation='vertical', spacing=dp(4))
        
        name_label = Label(
            text=self.plant_data.get('name', ''),
            font_size=sp(15),
            bold=True,
            color=COLORS['text_dark'],
            halign='right',
            valign='middle',
            size_hint_y=None,
            height=dp(28),
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        sci_name = Label(
            text=self.plant_data.get('scientific_name', ''),
            font_size=sp(11),
            color=COLORS['text_secondary'],
            halign='right',
            valign='middle',
            size_hint_y=None,
            height=dp(20),
            italic=True,
        )
        sci_name.bind(size=sci_name.setter('text_size'))
        
        # برچسب‌های ویژگی
        tags_layout = BoxLayout(orientation='horizontal', spacing=dp(6), size_hint_y=None, height=dp(24))
        
        # برچسب آبیاری
        water_tag = self._make_tag(
            f"💧 {self.plant_data.get('watering', '')}",
            COLORS['primary_light']
        )
        
        # برچسب سطح نگهداری
        care = self.plant_data.get('care_level', '')
        care_color = COLORS['secondary'] if 'آسان' in care else COLORS['warning'] if 'متوسط' in care else COLORS['error']
        care_tag = self._make_tag(f"⭐ {care}", care_color)
        
        tags_layout.add_widget(water_tag)
        tags_layout.add_widget(care_tag)
        tags_layout.add_widget(Widget())
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(sci_name)
        info_layout.add_widget(tags_layout)
        
        # دسته‌بندی
        cat_color = PLANT_CATEGORY_COLORS.get(self.plant_data.get('category', ''), COLORS['primary'])
        cat_label = Label(
            text=self.plant_data.get('category', ''),
            font_size=sp(10),
            color=cat_color,
            size_hint=(None, None),
            size=(dp(60), dp(20)),
            halign='center',
            bold=True,
        )
        
        right_col = BoxLayout(orientation='vertical', size_hint=(None, 1), width=dp(65))
        right_col.add_widget(cat_label)
        right_col.add_widget(Widget())
        
        # فلش
        arrow = Label(
            text='›',
            font_size=sp(24),
            color=COLORS['primary_light'],
            size_hint=(None, None),
            size=(dp(20), dp(30)),
        )
        right_col.add_widget(arrow)
        
        content.add_widget(img_container)
        content.add_widget(info_layout)
        content.add_widget(right_col)
        
        self.add_widget(content)
    
    def _make_tag(self, text, color):
        tag = Label(
            text=text,
            font_size=sp(10),
            color=color,
            size_hint=(None, None),
            size=(dp(75), dp(22)),
            bold=True,
        )
        return tag
    
    def _on_click(self, instance):
        if self.app_ref:
            self.app_ref.show_plant_detail(self.plant_data['id'])


class PlantImage(Widget):
    """ویجت تصویر گیاه: عکس واقعی در صورت وجود، وگرنه آیکون رنگی بر اساس دسته"""

    EMOJI_MAP = {
        'آپارتمانی': '🌿',
        'گلدار': '🌸',
        'دارویی': '🌱',
        'درخت میوه': '🍎',
    }

    def __init__(self, plant_name='', category='آپارتمانی', image_path=None,
                 corner_radius=None, **kwargs):
        super().__init__(**kwargs)
        self.plant_name = plant_name
        self.category = category
        self._fixed_radius = corner_radius
        self._photo = None
        self._emoji_label = None

        cat_color = PLANT_CATEGORY_COLORS.get(category, COLORS['primary'])

        with self.canvas:
            Color(*cat_color[:3], 0.18)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size,
                                         radius=[self._radius()])

        if image_path:
            inset = dp(3)
            self._inset = inset
            self._photo = Image(
                source=image_path,
                allow_stretch=True,
                keep_ratio=False,
                pos=self._inset_pos(),
                size=self._inset_size(),
            )
            self.add_widget(self._photo)
        else:
            emoji = self.EMOJI_MAP.get(category, '🌿')
            self._emoji_label = Label(
                text=emoji,
                font_size=sp(32),
                pos=self.pos,
                size=self.size,
                halign='center',
                valign='middle',
            )
            self.add_widget(self._emoji_label)

        self.bind(pos=self._update, size=self._update)

    def _radius(self):
        if self._fixed_radius is not None:
            return self._fixed_radius
        return dp(10)

    def _inset_pos(self):
        return (self.x + self._inset, self.y + self._inset)

    def _inset_size(self):
        return (max(1, self.width - self._inset * 2),
                max(1, self.height - self._inset * 2))

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.radius = [self._radius()]
        if self._photo:
            self._photo.pos = self._inset_pos()
            self._photo.size = self._inset_size()
        elif self._emoji_label:
            self._emoji_label.pos = self.pos
            self._emoji_label.size = self.size


class InfoRow(BoxLayout):
    """ردیف اطلاعات (کلیدـمقدار)"""
    
    def __init__(self, key, value, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = [dp(10), dp(5)]
        
        key_label = Label(
            text=key,
            font_size=sp(13),
            color=COLORS['text_secondary'],
            size_hint=(0.45, 1),
            halign='right',
            valign='middle',
        )
        key_label.bind(size=key_label.setter('text_size'))
        
        separator = Label(text=':', size_hint=(None, 1), width=dp(10), color=COLORS['divider'])
        
        value_label = Label(
            text=value,
            font_size=sp(13),
            color=COLORS['text_dark'],
            bold=True,
            size_hint=(0.55, 1),
            halign='left',
            valign='middle',
        )
        value_label.bind(size=value_label.setter('text_size'))
        
        self.add_widget(key_label)
        self.add_widget(separator)
        self.add_widget(value_label)


class BottomNavBar(BoxLayout):
    """نوار ناوبری پایین"""
    
    def __init__(self, app_ref=None, active_tab='home', **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.active_tab = active_tab
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(5), dp(5)]
        self.spacing = dp(0)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLORS['divider'])
            Line(points=[self.x, self.top, self.right, self.top], width=dp(1))
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _build(self):
        tabs = [
            ('home', '🏠', 'خانه'),
            ('plant_list', '🌿', 'گیاهان'),
            ('tools', '🔧', 'ابزارها'),
            ('shop', '🛒', 'فروشگاه'),
        ]
        
        for tab_id, icon, label in tabs:
            is_active = tab_id == self.active_tab
            color = COLORS['primary'] if is_active else COLORS['text_secondary']
            
            tab_btn = BoxLayout(orientation='vertical', spacing=dp(2))
            
            icon_label = Button(
                text=icon,
                font_size=sp(22),
                background_normal='',
                background_color=[0, 0, 0, 0],
                color=color,
                size_hint_y=None,
                height=dp(30),
            )
            
            text_label = Label(
                text=label,
                font_size=sp(10),
                color=color,
                bold=is_active,
                size_hint_y=None,
                height=dp(15),
            )
            
            tab_btn.add_widget(icon_label)
            tab_btn.add_widget(text_label)
            
            # رفتن به صفحه مربوطه
            _tab_id = tab_id
            icon_label.bind(on_press=lambda btn, t=_tab_id: self._navigate(t))
            
            self.add_widget(tab_btn)
    
    def _navigate(self, tab_id):
        if self.app_ref:
            self.app_ref.go_to_screen(tab_id)


class SectionTitle(Label):
    """عنوان بخش"""
    
    def __init__(self, text='', **kwargs):
        super().__init__(text=text, **kwargs)
        self.font_size = sp(17)
        self.bold = True
        self.color = COLORS['text_primary']
        self.size_hint_y = None
        self.height = dp(40)
        self.halign = 'right'
        self.valign = 'middle'
        self.bind(size=self.setter('text_size'))
