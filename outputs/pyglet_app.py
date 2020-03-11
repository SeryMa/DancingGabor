import pyglet

from outputs.output import Output
from utils.image import ArrayImage


class PygletOutput(Output):
    def __init__(self, get_next_frame, width, height, fps=30, **kwargs):
        super(PygletOutput, self).__init__(get_next_frame, **kwargs)

        self.window = pyglet.window.Window(width=width, height=height, resizable=True)
        self.frame_data = self.get_next_frame(0)
        self.arr_img = ArrayImage(self.frame_data)
        self.fps = fps

        @self.window.event
        def on_draw():
            self.window.clear()
            self.arr_img.set_array(self.frame_data)
            self.arr_img.image.blit(0, 0, width=width, height=height)

    def __update(self, dt=1):
        """ Updates the output handler

        Updates the frame data with new values.

        Parameters
        ----------
        dt: number
            Time in seconds from the last rendering of the window
        """
        self.frame_data = self.get_next_frame(dt)

    def run(self):
        pyglet.clock.schedule_interval(self.__update, 1.0 / self.fps)
        pyglet.app.run()
