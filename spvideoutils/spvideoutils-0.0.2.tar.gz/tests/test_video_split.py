from spvideoutils.video_split import main
import pytest

def test_video_split_default():
	"""By default it should print help and exit with -1."""
	with pytest.raises(SystemExit) as pytest_wrapped_e:
		main()
	assert pytest_wrapped_e.type == SystemExit
	assert pytest_wrapped_e.value.code == 2