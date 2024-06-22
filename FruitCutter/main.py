import cv2
import numpy as np
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import time

# Initialize hand detector
detector = HandDetector(maxHands=1, detectionCon=0.5)

# Load images and resize them
watermelon = cv2.imread('watermelon.png', cv2.IMREAD_UNCHANGED)
bomb = cv2.imread('bomb.png', cv2.IMREAD_UNCHANGED)
watermelon = cv2.resize(watermelon, (150, 162))  # Resize to smaller size
bomb = cv2.resize(bomb, (100, 100))  # Resize to smaller size

class Fruit:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.x = random.randint(400, 880)  # Spawn around the center
        self.y = 720  # Spawn from the bottom
        self.speed_x = random.uniform(-5, 5)  # Initial horizontal speed
        self.speed_y = random.uniform(-25, -20)  # Initial vertical speed (upwards)
        self.gravity = 0.5  # Gravity effect
        self.width = self.image.shape[1]
        self.height = self.image.shape[0]
        self.max_height = random.uniform(0.2 * 720, 0.4 * 720)  # Maximum height between 60-80% of the screen height

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity  # Apply gravity
        if self.y < self.max_height:
            self.speed_y *= -1  # Reverse direction when reaching maximum height

    def draw(self, img):
        if 0 <= self.y < img.shape[0] and 0 <= self.x < img.shape[1]:
            img = cvzone.overlayPNG(img, self.image, [int(self.x), int(self.y)])
        return img

def draw_button(img, pos, size, text, hover):
    x, y = pos
    w, h = size
    if hover:
        cv2.rectangle(img, pos, (x+w, y+h), (0, 255, 0), cv2.FILLED)
    else:
        cv2.rectangle(img, pos, (x+w, y+h), (0, 0, 255), cv2.FILLED)
    cv2.putText(img, text, (x+20, y+int(h/1.5)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

def is_hovering(lmList, pos, size):
    x, y = pos
    w, h = size
    if lmList:
        index_tip = lmList[8]
        if x < index_tip[0] < x + w and y < index_tip[1] < y + h:
            return True
    return False

# Create game window
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Initialize variables
fruits = []
score = 0
game_over = False
start_game = False
start_time = None
button_hover_start = None
button_size = (400, 100)
button_pos = (440, 310)

# Game loop
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=False)

    if not start_game:
        # Title screen
        draw_button(img, button_pos, button_size, 'Start Game', False)
        if hands and is_hovering(hands[0]['lmList'], button_pos, button_size):
            if not button_hover_start:
                button_hover_start = time.time()
            if time.time() - button_hover_start > 2:
                start_game = True
                button_hover_start = None
        else:
            button_hover_start = None
    elif game_over:
        # End screen
        draw_button(img, button_pos, button_size, 'Replay', False)
        cv2.putText(img, 'You Lose', (500, 200), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
        if hands and is_hovering(hands[0]['lmList'], button_pos, button_size):
            if not button_hover_start:
                button_hover_start = time.time()
            if time.time() - button_hover_start > 2:
                game_over = False
                start_game = True
                score = 0
                fruits = []
                button_hover_start = None
        else:
            button_hover_start = None
    else:
        # Main game
        # Add new fruit
        if random.randint(0, 100) < 2:
            if random.randint(0, 1) == 0:
                fruits.append(Fruit(watermelon, 'watermelon'))
            else:
                fruits.append(Fruit(bomb, 'bomb'))

        # Move and draw fruits
        for fruit in fruits[:]:
            fruit.move()
            img = fruit.draw(img)

            # Remove fruits that are off the screen
            if fruit.y > 720:
                fruits.remove(fruit)

            # Check for collision with finger
            if hands:
                lmList = hands[0]['lmList']
                index_tip = lmList[8]
                cv2.circle(img, (index_tip[0], index_tip[1]), 15, (255, 0, 255), cv2.FILLED)

                if fruit.x < index_tip[0] < fruit.x + fruit.width and fruit.y < index_tip[1] < fruit.y + fruit.height:
                    if fruit.type == 'watermelon':
                        score += 1
                    else:
                        game_over = True
                    fruits.remove(fruit)

        # Display score
        cv2.putText(img, f'Score: {score}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)

    # Show frame
    cv2.imshow('Fruit Ninja', img)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
