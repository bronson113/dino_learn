from dino_game_api import dino_game
import time

def main():
    current_game=dino_game()
    fps=0.0
    while current_game.playcount>0:
        last_time=time.time()
        current_game.logic()
        current_game.coded_rule()
        fps=1/(time.time()-last_time)
        print('fps: {}'.format(fps))

if __name__ == '__main__':
    main()
