from os import listdir, chdir

from cv2 import VideoCapture, imwrite, CAP_PROP_POS_FRAMES

if __name__ == '__main__':
    # for folder in ['spectra']:
    for folder in listdir('.'):
        chdir(folder)

        for video_file in (video_file for video_file in listdir('.') if video_file.endswith('.avi')):
            for fr in [0, 15, 30]:
                cap = VideoCapture(video_file)
                cap.set(CAP_PROP_POS_FRAMES, fr)
                ret, frame = cap.read()

                imwrite(f'frame_{fr}_{video_file[:-4]}.png', frame)

        chdir('..')
