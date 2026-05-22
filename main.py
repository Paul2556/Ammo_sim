import arcade

WIDTH = 1280
HEIGHT = 720

class Game(arcade.Window):

    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Missile Simulator")

    def on_draw(self):
        self.clear()

    def on_update(self, delta_time):
        pass

def main():
    game = Game()
    arcade.run()

if __name__ == "__main__":
    main()