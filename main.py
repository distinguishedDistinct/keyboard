# main.py
import cv2
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from cvzone.HandTrackingModule import HandDetector

class Button:
    def __init__(self, pos, text, size=(120, 110)):
        self.pos = pos
        self.size = size
        self.text = text
        self.color = (128, 0, 0)  # Default color
        self.prev_click_state = False
        self.last_click_time = 0

    def draw(self, img, alpha=0.5, lmList=None):
        x, y = self.pos
        w, h = self.size

        img_copy = img.copy()
        overlay = img_copy.copy()

        cv2.rectangle(overlay, self.pos, (x + w, y + h), (139, 128, 0), 4)  # Add this line for border

        if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
            self.color = (0, 255, 0)
            cv2.rectangle(overlay, self.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)

        else:
            self.color = (128, 0, 0)
            cv2.rectangle(overlay, self.pos, (x + w, y + h), self.color, cv2.FILLED)

        cv2.putText(overlay, self.text, (x + 25, y + 75), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)

        cv2.addWeighted(overlay, alpha, img_copy, 1 - alpha, 0, img_copy)
        return img_copy

    def is_clicked(self, lmList):
        return (
            self.pos[0] < lmList[8][0] < self.pos[0] + self.size[0] and self.pos[1] < lmList[8][1] < self.pos[1] + self.size[1]
            and self.pos[0] < lmList[12][0] < self.pos[0] + self.size[0] and self.pos[1] < lmList[12][1] < self.pos[1] + self.size[1]
        )

class HandTrackingApp(App):
    def build(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.detector = HandDetector(detectionCon=0.8)

        self.layout = BoxLayout(orientation='vertical')

        self.text_input = TextInput(font_size=24, multiline=False, size_hint_y=0.4)  #text box size
        self.layout.add_widget(self.text_input)

        self.image_widget = Image()
        self.layout.add_widget(self.image_widget)

        self.button_positions = [
            [50 + i * 120, 80] for i in range(10)
        ] + [
            [50 + i * 120, 210] for i in range(9)
        ] + [
            [50 + i * 120, 340] for i in range(7)
        ]

        self.capital_button_texts = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.original_button_texts = "qwertyuiopasdfghjklzxcvbnm"
        self.special_button_texts = "1234567890-=!@#$%^&*()_+[]{}|;':\",./<>?"

        self.original_buttons = [Button(pos, text) for pos, text in zip(self.button_positions, self.original_button_texts)]
        self.capital_buttons = [Button(pos, text) for pos, text in zip(self.button_positions, self.capital_button_texts)]
        self.special_buttons = [Button(pos, text) for pos, text in zip(self.button_positions, self.special_button_texts)]

        space_button_position = [100, 470]
        space_button_text = " "
        self.space_button = Button(space_button_position, space_button_text, size=(400, 100))
        self.original_buttons.append(self.space_button)
        self.capital_buttons.append(self.space_button)


        backspace_button_position = [800, 470]
        backspace_button_text = "back"
        self.backspace_button = Button(backspace_button_position, backspace_button_text, size=(300, 100))
        self.original_buttons.append(self.backspace_button)
        self.capital_buttons.append(self.backspace_button)

        caps_button_position = [910, 580]
        caps_button_text = "Caps"
        self.caps_button = Button(caps_button_position, caps_button_text, size=(300, 110))
        self.special_buttons.append(self.caps_button)

        switch_button_position = [450, 580]
        switch_button_text = "switch"
        self.switch_button = Button(switch_button_position, switch_button_text, size=(400, 110))
        self.original_buttons.append(self.switch_button)
        
        enter_button_position = [910, 340]
        enter_button_text = "ENT"
        self.enter_button = Button(enter_button_position, enter_button_text, size=(300, 110))
        self.original_buttons.append(self.enter_button)
        self.capital_buttons.append(self.enter_button)


        # Create switch button for the second keyboard
        switch_button_position_2 = [500, 590]
        switch_button_text_2 = "switch"
        self.switch_button_2 = Button(switch_button_position_2, switch_button_text_2, size=(350, 100))
        self.special_buttons.append(self.switch_button_2)


        # Create Capslock button for the third keyboard
        caps_button_position_2 = [450, 580]
        caps_button_text_2 = "Caps"
        self.caps_button_2 = Button(caps_button_position_2, caps_button_text_2, size=(300, 110))
        self.capital_buttons.append(self.caps_button_2)

        # Flag to track which keyboard is active
        self.current_key = None 
        self.is_original_keyboard = True
        self.is_second_keyboard = False
        self.is_capital_keyboard = False

        return self.layout

    def update(self, dt):
        success, img = self.cap.read()
        hands, img = self.detector.findHands(img)

        if hands:
            lmList = hands[0]["lmList"]
            clicked_key = self.detect_key(lmList)

            if clicked_key is not None:
                if clicked_key == "back":
                    self.backspace()
                elif clicked_key == "Caps":
                    self.capslock()
                elif clicked_key == "switch":
                    self.switch_keyboard()
                elif clicked_key == "ENT":
                    self.enter_key()

                elif clicked_key != self.current_key:
                    self.text_input.text += clicked_key
                    self.current_key = clicked_key

            if self.is_original_keyboard:
                active_buttons = self.original_buttons

            elif self.is_second_keyboard:
                active_buttons = self.special_buttons
            else:
                active_buttons = self.capital_buttons

            for button in active_buttons:
                img = button.draw(img, alpha=0.5, lmList=lmList)

        buf1 = cv2.flip(img, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.image_widget.texture = texture

    def detect_key(self, lmList):
        if self.is_original_keyboard:
            active_buttons = self.original_buttons

        elif self.is_second_keyboard:
            active_buttons = self.special_buttons
        else:
            active_buttons = self.capital_buttons

        for button in active_buttons:
            if button.is_clicked(lmList):
                return button.text
        return None

    def is_backspace_clicked(self, lmList):
        return (
            self.backspace_button.pos[0] < lmList[8][0] < self.backspace_button.pos[0] + self.backspace_button.size[0]
            and self.backspace_button.pos[1] < lmList[8][1] < self.backspace_button.pos[1] + self.backspace_button.size[1]
            and self.backspace_button.pos[0] < lmList[12][0] < self.backspace_button.pos[0] + self.backspace_button.size[0]
            and self.backspace_button.pos[1] < lmList[12][1] < self.backspace_button.pos[1] + self.backspace_button.size[1]
        )

    def backspace(self):
        current_time = time.time()
        if current_time - self.backspace_button.last_click_time > 0.6:
            current_text = self.text_input.text
            if len(current_text) > 0:
                self.text_input.text = current_text[:-1]
            self.backspace_button.last_click_time = current_time

    def space(self):
        current_time = time.time()
        if current_time - self.space_button.last_click_time > 0.6:
            self.text_input.text += ' '
            self.space_button.last_click_time = current_time

    def enter_key(self):
        current_time = time.time()
        if current_time - self.enter_button.last_click_time > 2.0:
            self.text_input.text += '\n'
            self.enter_button.last_click_time = current_time
                

    def switch_keyboard(self):
        current_time = time.time()
        if current_time - self.switch_button.last_click_time > 1.5:
            if self.is_original_keyboard:
                self.is_second_keyboard = True
                self.is_original_keyboard = False
                print("Switching to Second Keyboard")
            
            else:
                self.is_original_keyboard = True
                self.is_capital_keyboard = False
                print("Switching to Original Keyboard")

            self.switch_button.last_click_time = current_time

    def capslock(self):
        current_time = time.time()
        if current_time - self.caps_button.last_click_time > 1.5:
            if self.is_second_keyboard:
                self.is_capital_keyboard = True
                self.is_second_keyboard = False
                print("Switching to Capital Keyboard")
            else:
                self.is_original_keyboard = True
                self.is_capital_keyboard = False
                print("Switching to Second Keyboard")

            self.caps_button.last_click_time = current_time



    def on_start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_stop(self):
        self.cap.release()

if __name__ == '__main__':
    HandTrackingApp().run()
