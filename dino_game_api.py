import cv2
import keyboard
import math
import mss
import numpy as np
import random
import time
import threading
from PIL import Image

class obstacle_temp():
    def __init__(self, path_to_img, threshold, height, width):
        self.temp=cv2.imread(path_to_img,0)
        self.threshold=threshold
        self.h=height
        self.w=width

    def match_temp(self, img):
        obs=[]
        res = cv2.matchTemplate(img, self.temp, cv2.TM_SQDIFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
        matching_loc = np.where(res <= self.threshold)
        for (x,y) in zip(matching_loc[1], matching_loc[0]):
            obs.append([x,y,self.h,self.w])
        return obs


class dino_game():

    def __init__(self):
        self.alive=True
        self.shooter=mss.mss()
        self.playcount=5
        self.temp_dino_up=cv2.imread('./matching_temp/dinosure_1.png',0)
        self.temp_dino_down=cv2.imread('./matching_temp/dinosure_2.png',0)
        self.temp_reset=cv2.imread('./matching_temp/reset.png',0)
        self.temp_obs=[]
        self.temp_obs.append(obstacle_temp('./matching_temp/bird_up.png',0.1,44,32))
        self.temp_obs.append(obstacle_temp('./matching_temp/bird_down.png',0.1,46,30))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_0.png',0.07,25,34))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_1.png',0.05,25,23))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_2.png',0.1,35,25))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_3.png',0.1,50,37))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_4.png',0.20,51,26))
        self.temp_obs.append(obstacle_temp('./matching_temp/catus_5.png',0.1,75,40))
        while(not self.get_game_location):
            time.sleep(2)
        print('found, game feild: {}'.format(self.game_field))
        self.jump
        random.seed(time.time())
        self.init_time=time.time()

    @property
    def get_field(self):
        self.field = self.shooter.grab(self.game_field)
        self.field = Image.frombytes('RGB', self.field.size, self.field.rgb).convert('L')
        self.field = np.array(self.field)
        (thresh, self.field) = cv2.threshold(self.field, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        if self.field[0][0] == 0:
             self.field = cv2.bitwise_not(self.field)

    @property
    def get_game_location(self):
        self.field = self.shooter.grab(self.shooter.monitors[1])
        self.field = Image.frombytes('RGB', self.field.size, self.field.rgb).convert('L')
        self.field = np.array(self.field)
        (thresh, self.field) = cv2.threshold(self.field, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        res = cv2.matchTemplate(self.field, self.temp_reset, cv2.TM_SQDIFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
        if min_val < 0.1:
            self.game_field={"left":min_loc[0]-315, "top": min_loc[1]-110, "width": 630, "height": 180}
            return True

        res = cv2.matchTemplate(self.field, self.temp_dino_up, cv2.TM_SQDIFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
        if min_val < 0.1:
            self.game_field={"left":min_loc[0]-20, "top": min_loc[1]-120, "width": 630, "height": 180}
            return True

        return False



    @property
    def check_game_over(self):
        res = cv2.matchTemplate(self.field, self.temp_reset, cv2.TM_SQDIFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
        if min_val < 0.1:
            self.alive=False

    @property
    def get_dino_pos(self):
        res = cv2.matchTemplate(self.field, self.temp_dino_up, cv2.TM_SQDIFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
        self.dino_pos=min_loc
        self.dino_pos=np.array(self.dino_pos)
        if min_val > 0.1:
            res = cv2.matchTemplate(self.field, self.temp_dino_down, cv2.TM_SQDIFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
            self.dino_pos=np.array(min_loc) - np.array([2,17])

    @property
    def get_all_obs(self):
        obj=[]
        all_obs=[]
        for i in self.temp_obs:
            all_obs.append(i.match_temp(self.field))
        for i in all_obs:
            for j in i:
                obj.append(j)
        obj.sort()
        self.obj=obj

    def coded_rule(self):
        thread_1=threading.Thread(target = self.get_all_obs).start()
        if thread_1:
            thread_1.join()

        if len(self.obj) > 0:
            if self.obj[0][0] < 100 - self.obj[0][2]:
                self.ground
                return
            if self.obj[0][0] < 200 + self.current_time and self.obj[0][1] > 60 :
                self.jump
                return

    def restart(self):
        self.jump
        self.ground
        print(self.current_time)
        self.alive=True
        self.playcount -= 1
        print(self.playcount)

    def logic(self):
        self.current_time=time.time()-self.init_time
        self.get_field
        self.check_game_over
        if not self.alive:
            self.init_time = time.time()
            output = self.restart()

    @property
    def jump(self):
        keyboard.release('down')
        keyboard.press('space')

    @property
    def ground(self):
        keyboard.press('down')
        keyboard.release('space')

def main():
    fps=0.0
    time.sleep(5)
    current_game=dino_game()
    while(current_game.playcount > 0):
        last_time=time.time()
        current_game.logic()
        current_game.coded_rule()
        fps=1/(time.time()-last_time)
        print('fps: {}'.format(fps))

if __name__ == "__main__":
  main()
