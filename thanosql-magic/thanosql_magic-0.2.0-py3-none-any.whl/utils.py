import matplotlib.pyplot as plt
from IPython.display import Audio, Video, display
from matplotlib.pyplot import imread


def print_image(df, print_option):
    w = 40
    h = 40
    fig = plt.figure(figsize=(w, h))

    column_name = df.columns[0]

    num_cols = 5
    num_rows = 5
    df = df[: num_cols * num_rows]
    for idx, img_path in enumerate(df[column_name]):
        image = imread(img_path)
        fig.add_subplot(num_rows, num_cols, idx + 1)
        plt.axis("off")
        plt.title(img_path, fontdict={"fontsize": 50 / num_cols})
        plt.imshow(image)
    plt.show()
    return


def print_audio(df, print_option):
    column_name = df.columns[0]
    audio_file_list = list(df[column_name])

    ### display 5 videos max
    limit = 5
    for audio in audio_file_list[:limit]:
        print(audio)
        display(Audio(audio))
    return


def print_video(df, print_option):
    column_name = df.columns[0]
    video_file_list = list(df[column_name])

    ### display 5 videos max
    limit = 5
    for video in video_file_list[:limit]:
        print(video)
        display(Video(video, embed=True))
    return
