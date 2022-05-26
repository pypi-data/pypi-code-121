from analysis_utils.visualization import (
    show_10_images_and_captions_grid,
)
from src.data_utils.save_and_load_data import (
    load_representations_captions_images,
    load_idx_word_dicts,
)

if __name__ == "__main__":
    _, captions_test, images_test = load_representations_captions_images("test")
    idx_to_word, _ = load_idx_word_dicts()

    show_10_images_and_captions_grid(
        images_test, captions_test, idx_to_word, file_name="example_images.png"
    )
