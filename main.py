import requests
import json
import webbrowser
import os
from kivy.core.audio import SoundLoader
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatIconButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import Clock

FIREBASE_URL = "https://mypingo-a693f-default-rtdb.firebaseio.com"

class ParentApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.last_audio_time = 0 
        self.sound = None
        self.current_lat = None
        
        screen = MDScreen()
        main_layout = MDBoxLayout(orientation='vertical')
        
        self.toolbar = MDTopAppBar(title="Pingo Parent Control", elevation=4)
        main_layout.add_widget(self.toolbar)
        
        content = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # כרטיס מיקום
        loc_card = MDCard(orientation='vertical', padding=15, size_hint=(1, None), height=180, elevation=2, radius=[15])
        loc_card.add_widget(MDLabel(text="📍 Child Location", font_style="H6", bold=True))
        self.loc_label = MDLabel(text="Waiting for sync...", theme_text_color="Secondary")
        loc_card.add_widget(self.loc_label)
        self.map_btn = MDFillRoundFlatIconButton(icon="google-maps", text="OPEN MAP", on_release=self.open_maps, disabled=True)
        loc_card.add_widget(self.map_btn)
        content.add_widget(loc_card)
        
        # כרטיס האזנה
        listen_card = MDCard(orientation='vertical', padding=15, size_hint=(1, None), height=150, elevation=2, radius=[15])
        listen_card.add_widget(MDLabel(text="🎙️ Live Listening", font_style="H6", bold=True))
        self.status_icon = MDLabel(text="Status: Idle", theme_text_color="Hint")
        listen_card.add_widget(self.status_icon)
        self.record_btn = MDRaisedButton(text="START LISTENING", size_hint=(1, None), on_release=self.toggle_listening)
        listen_card.add_widget(self.record_btn)
        content.add_widget(listen_card)
        
        # כפתור איפוס SOS
        self.reset_sos_btn = MDRaisedButton(text="CLEAR SOS ALERT", pos_hint={'center_x': .5}, on_release=self.clear_sos, opacity=0)
        content.add_widget(self.reset_sos_btn)
        
        main_layout.add_widget(content)
        screen.add_widget(main_layout)
        
        Clock.schedule_interval(self.update_ui, 2)
        Clock.schedule_interval(self.check_for_audio, 0.5)
        return screen

    def update_ui(self, *args):
        try:
            data = requests.get(f"{FIREBASE_URL}/child_status.json").json()
            if data:
                # עדכון מיקום
                self.current_lat, self.current_lng = data.get("lat"), data.get("lng")
                self.loc_label.text = f"Lat: {self.current_lat:.4f}, Lng: {self.current_lng:.4f}\nLast seen: {data.get('last_seen')}"
                self.map_btn.disabled = False
                
                # בדיקת SOS
                if data.get("sos") == True:
                    self.toolbar.md_bg_color = (1, 0, 0, 1)
                    self.toolbar.title = "!!! SOS EMERGENCY !!!"
                    self.reset_sos_btn.opacity = 1
        except: pass

    def clear_sos(self, *args):
        requests.patch(f"{FIREBASE_URL}/child_status.json", data=json.dumps({"sos": False}))
        self.toolbar.md_bg_color = self.theme_cls.primary_color
        self.toolbar.title = "Pingo Parent Control"
        self.reset_sos_btn.opacity = 0

    def open_maps(self, *args):
        webbrowser.open(f"https://www.google.com/maps?q={self.current_lat},{self.current_lng}")

    def check_for_audio(self, *args):
        if self.record_btn.text == "STOP LISTENING" and os.path.exists("live_audio.wav"):
            try:
                mtime = os.path.getmtime("live_audio.wav")
                if mtime > self.last_audio_time:
                    self.last_audio_time = mtime
                    if self.sound: self.sound.stop(); self.sound.unload()
                    self.sound = SoundLoader.load("live_audio.wav")
                    if self.sound: self.sound.play()
            except: pass

    def toggle_listening(self, *args):
        is_starting = self.record_btn.text == "START LISTENING"
        requests.patch(f"{FIREBASE_URL}/commands.json", data=json.dumps({"record_now": is_starting}))
        self.record_btn.text = "STOP LISTENING" if is_starting else "START LISTENING"
        self.record_btn.md_bg_color = (0.9, 0.2, 0.2, 1) if is_starting else self.theme_cls.primary_color
        self.status_icon.text = "Status: Recording..." if is_starting else "Status: Idle"

if __name__ == "__main__":
    ParentApp().run()