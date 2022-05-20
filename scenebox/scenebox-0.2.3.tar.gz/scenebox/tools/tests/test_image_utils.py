from ...tools.image_utils import ImageSequence


def test_image_sequence_1():
    img_seq = ImageSequence(
        sensor="sensor",
        width=100,
        height=100,
        image_format="png"
    )
    img_seq.add_image(image_uri="test_uri", timestamp=1.0, image_id="image_id")
    assert img_seq.fps_max is None
    assert img_seq.start_time == 1.0
    assert img_seq.end_time == 1.0
    assert img_seq.fps_mean is None


def test_image_sequence_2():
    img_seq = ImageSequence(
        sensor="sensor",
        width=100,
        height=100,
        image_format="png"
    )
    img_seq.add_image(image_uri="test_uri_1", timestamp=1.0, image_id="image_id_1")
    img_seq.add_image(image_uri="test_uri_2", timestamp=2.0, image_id="image_id_2")
    assert img_seq.fps_max == 1.0
    assert img_seq.start_time == 1.0
    assert img_seq.end_time == 2.0
    assert img_seq.fps_mean == 1.0

