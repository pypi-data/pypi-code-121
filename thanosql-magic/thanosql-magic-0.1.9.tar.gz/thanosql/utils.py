import matplotlib.pyplot as plt
from ipywidgets import Audio, Video
from matplotlib.pyplot import imread


def print_image(df, print_option):
    w = 40
    h = 40
    fig = plt.figure(figsize=(w, h))
    columns = 10

    column = df.columns[0]
    rows = int(len(df[column]) / columns) + 1
    for i, img_path in enumerate(df[column]):
        image = imread(img_path)
        fig.add_subplot(rows, columns, i + 1)
        plt.axis("off")
        plt.imshow(image)
    plt.show()
    return


def print_audio(df, print_option):
    column = df.columns[0]
    audio_file = df[column][0]
    audio = Audio.from_file(audio_file)
    return audio


def print_video(df, print_option):
    column = df.columns[0]
    video_file = df[column][0]
    video = Video.from_file(video_file)
    return video
