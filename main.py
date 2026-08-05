"""
Plant Care App - برنامه مراقبت از گیاهان
فریمورک: Kivy
"""

import os
import sys

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import (StringProperty, NumericProperty, BooleanProperty, 
                              ListProperty, ObjectProperty, DictProperty)
from kivy.storage.jsonstore import JsonStore
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

import json
import time
import threading
from datetime import datetime, timedelta

# تنظیم اندازه پنجره برای شبیه‌سازی موبایل
Window.size = (390, 844)
Window.clearcolor = get_color_from_hex('#F0F7F0')

# رنگ‌های برنامه
COLORS = {
    'primary': get_color_from_hex('#2E7D32'),       # سبز تیره
    'primary_light': get_color_from_hex('#4CAF50'),  # سبز روشن
    'primary_dark': get_color_from_hex('#1B5E20'),   # سبز خیلی تیره
    'secondary': get_color_from_hex('#8BC34A'),      # سبز روشن‌تر
    'accent': get_color_from_hex('#FF6F00'),          # نارنجی
    'background': get_color_from_hex('#F1F8E9'),     # سبز خیلی کم‌رنگ
    'card': get_color_from_hex('#FFFFFF'),            # سفید
    'text_primary': get_color_from_hex('#1B5E20'),   # سبز تیره برای متن
    'text_secondary': get_color_from_hex('#558B2F'),  # سبز متوسط
    'text_dark': get_color_from_hex('#212121'),      # خاکستری تیره
    'divider': get_color_from_hex('#C8E6C9'),        # سبز خیلی کم‌رنگ
    'warning': get_color_from_hex('#F9A825'),        # زرد
    'error': get_color_from_hex('#C62828'),          # قرمز
    'white': get_color_from_hex('#FFFFFF'),
    'ad_bg': get_color_from_hex('#FFF9C4'),          # زرد کمرنگ برای تبلیغات
}

# لود دیتابیس
from data.plants_db import PLANTS_DATA, SHOP_CATEGORIES, get_plant_by_id, search_plants

# لود صفحات
from screens.home_screen import HomeScreen
from screens.plant_list_screen import PlantListScreen
from screens.plant_detail_screen import PlantDetailScreen
from screens.tools_screen import ToolsScreen
from screens.timer_screen import TimerScreen
from screens.ai_vet_screen import AIVetScreen
from screens.shop_screen import ShopScreen
from screens.add_plant_screen import AddPlantScreen
from screens.search_screen import SearchScreen


class PlantCareApp(App):
    """کلاس اصلی برنامه مراقبت از گیاهان"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'گیاهیار - مراقبت از گیاهان'
        self.icon = 'images/app_icon.png'
        
        # ذخیره‌سازی داده‌ها
        self.store = JsonStore('plant_care_data.json')
        self.custom_plants_store = JsonStore('custom_plants.json')
        
        # داده‌های برنامه
        self.all_plants = list(PLANTS_DATA)
        self.load_custom_plants()
        
        # مدیریت صفحات
        self.current_plant = None
        self.screen_manager = None
    
    def build(self):
        """ساخت UI برنامه"""
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # اضافه کردن تمام صفحات
        screens = [
            HomeScreen(name='home'),
            PlantListScreen(name='plant_list'),
            PlantDetailScreen(name='plant_detail'),
            ToolsScreen(name='tools'),
            TimerScreen(name='timers'),
            AIVetScreen(name='ai_vet'),
            ShopScreen(name='shop'),
            AddPlantScreen(name='add_plant'),
            SearchScreen(name='search'),
        ]
        
        for screen in screens:
            screen.app = self
            self.screen_manager.add_widget(screen)
        
        # صفحه اول
        self.screen_manager.current = 'home'
        
        return self.screen_manager
    
    def load_custom_plants(self):
        """لود گیاهان اضافه شده توسط کاربر"""
        try:
            if self.custom_plants_store.exists('plants'):
                custom = self.custom_plants_store.get('plants')['data']
                self.all_plants.extend(custom)
        except Exception as e:
            print(f"خطا در لود گیاهان: {e}")
    
    def add_custom_plant(self, plant_data):
        """اضافه کردن گیاه جدید توسط کاربر"""
        plant_data['id'] = len(self.all_plants) + 1000
        plant_data['image'] = 'default_plant.jpg'
        self.all_plants.append(plant_data)
        
        try:
            existing = []
            if self.custom_plants_store.exists('plants'):
                existing = self.custom_plants_store.get('plants')['data']
            existing.append(plant_data)
            self.custom_plants_store.put('plants', data=existing)
        except Exception as e:
            print(f"خطا در ذخیره گیاه: {e}")
    
    def go_to_screen(self, screen_name, direction='left'):
        """رفتن به صفحه مشخص"""
        self.screen_manager.transition.direction = direction
        self.screen_manager.current = screen_name
    
    def go_back(self):
        """برگشت به صفحه قبل"""
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'home'
    
    def show_plant_detail(self, plant_id):
        """نمایش جزئیات گیاه"""
        plant = get_plant_by_id(plant_id)
        if not plant:
            # جستجو در گیاهان سفارشی
            for p in self.all_plants:
                if p['id'] == plant_id:
                    plant = p
                    break
        
        if plant:
            self.current_plant = plant
            detail_screen = self.screen_manager.get_screen('plant_detail')
            detail_screen.load_plant(plant)
            self.go_to_screen('plant_detail')
    
    def on_start(self):
        """شروع برنامه"""
        print("🌱 گیاهیار راه‌اندازی شد!")
        # چک کردن تایمرها
        Clock.schedule_interval(self.check_timers, 60)
    
    def check_timers(self, dt):
        """چک کردن تایمرهای منقضی شده"""
        try:
            # هر بار یک JsonStore تازه می‌سازیم تا مطمئن باشیم آخرین
            # تایمرهای ذخیره‌شده (حتی آن‌هایی که همین الان اضافه شده‌اند) دیده می‌شوند
            fresh_store = JsonStore('timers_data.json')
            if fresh_store.exists('timers'):
                timers = fresh_store.get('timers')['data']
                now = datetime.now()
                for timer in timers:
                    if timer.get('active') and timer.get('next_time'):
                        next_time = datetime.fromisoformat(timer['next_time'])
                        if now >= next_time:
                            self.show_timer_notification(timer['name'])
        except Exception as e:
            print(f"خطا در چک تایمر: {e}")
    
    def show_timer_notification(self, timer_name):
        """نمایش اعلان تایمر"""
        popup_content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        icon_label = Label(text='⏰', font_size=sp(48), size_hint_y=None, height=dp(60))
        title = Label(
            text=f'زمان: {timer_name}!',
            font_size=sp(18),
            bold=True,
            color=COLORS['primary'],
        )
        msg = Label(
            text='وقت مراقبت از گیاهتان رسیده است',
            font_size=sp(14),
            color=COLORS['text_secondary'],
        )
        
        ok_btn = Button(
            text='باشه',
            size_hint_y=None,
            height=dp(45),
            background_color=COLORS['primary'],
            color=COLORS['white'],
        )
        
        popup_content.add_widget(icon_label)
        popup_content.add_widget(title)
        popup_content.add_widget(msg)
        popup_content.add_widget(ok_btn)
        
        popup = Popup(
            title='یادآوری گیاه',
            content=popup_content,
            size_hint=(0.85, 0.4),
            auto_dismiss=False,
        )
        
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()


if __name__ == '__main__':
    PlantCareApp().run()
