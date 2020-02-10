import pyglet
from pyglet.window import key

from outputs.output import Output
from utils.array import ArrayImage


class PygletOutput(Output):
    def __init__(self, get_next_frame, width, height, **kwargs):
        super(PygletOutput, self).__init__(get_next_frame, **kwargs)

        self.window = pyglet.window.Window(width=width, height=height, resizable=True)
        self.frame_data = self.get_next_frame(0)
        self.arr_img = ArrayImage(self.frame_data)

        @self.window.event
        def on_draw():
            self.window.clear()
            self.arr_img.set_array(self.frame_data)
            self.arr_img.image.blit(0, 0, width=width, height=height)

        @self.window.event
        def on_text_motion(motion):
            x = y = 0
            if motion == key.MOTION_UP:
                x += 1
            elif motion == key.MOTION_DOWN:
                x -= 1
            elif motion == key.MOTION_LEFT:
                y -= 1
            elif motion == key.MOTION_RIGHT:
                y += 1
            else:
                pass

    def __update(self, dt=1):
        """
        :param dt: time in seconds from the last rendering of the window
        """
        self.frame_data = self.get_next_frame(dt)

    def run(self, clock_interval=40.0, **kwargs):
        pyglet.clock.schedule_interval(self.__update, 1.0 / clock_interval)
        pyglet.app.run()


