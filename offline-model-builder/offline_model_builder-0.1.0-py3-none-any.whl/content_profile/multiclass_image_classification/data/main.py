
from utils.remove_duplicate import remove_duplicate
from utils.extract_frames import extract_frame

# Press the green button in the gutter to run the script.
file_path = 'data/travel.mp4'
if __name__ == '__main__':
    extract_frame(file_path)
    remove_duplicate(file_path)

