import numpy as np
import pyglet

from outputs.pyglet_app import PygletOutput
from utils.image import ArrayImage


class PygletDiffOutput(PygletOutput):
    def __init__(self, get_next_frame, width, height, fps=30, **kwargs):
        super(PygletDiffOutput, self).__init__(get_next_frame, width, height, fps, **kwargs)

        self.diff_window = pyglet.window.Window(width=width, height=height, resizable=True)
        self.diff = np.zeros((width, height))
        self.diff_arr_img = ArrayImage(self.diff)
        self.last = self.frame_data.copy()

        @self.diff_window.event
        def on_draw():
            self.diff_window.clear()
            self.diff_arr_img.set_array(self.diff)
            self.diff_arr_img.image.blit(0, 0, width=width, height=height)

    def __update(self, dt=1):
        """ Updates the output handler

        Updates the frame data with new values.

        Parameters
        ----------
        dt: number
            Time in seconds from the last rendering of the window
        """
        self.diff = self.last - self.frame_data
        self.last = self.frame_data.copy()

    def run(self):
        pyglet.clock.schedule_interval(self.__update, 1.0 / self.fps)

        super(PygletDiffOutput, self).run()
        # pyglet.app.run()
