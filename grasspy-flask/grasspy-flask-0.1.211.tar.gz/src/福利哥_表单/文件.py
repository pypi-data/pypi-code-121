从 无敌表单 导入 〇文件字段 为 _〇文件字段
从 无敌表单.验证器 导入 〇需要数据
from werkzeug.datastructures import FileStorage
from wtforms.validators import StopValidation
从 flask_wtf.file 导入 FileAllowed, FileSize

class 〇文件字段(_〇文件字段):
    """Werkzeug-aware subclass of :class:`wtforms.fields.FileField`."""

    def process_formdata(self, valuelist):
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = next(valuelist, None)

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()


class 〇需要文件(〇需要数据):
    """Validates that the data is a Werkzeug
    :class:`~werkzeug.datastructures.FileStorage` object.

    :param message: error message

    You can also use the synonym ``file_required``.
    """

    def __call__(self, form, field):
        if not (isinstance(field.data, FileStorage) and field.data):
            raise StopValidation(
                self.消息 or field.gettext("This field is required.")
            )


需要文件 = 〇需要文件

类 〇允许文件(FileAllowed):
    """Validates that the uploaded file is allowed by a given list of
    extensions or a Flask-Uploads :class:`~flaskext.uploads.UploadSet`.

    :param upload_set: A list of extensions or an
        :class:`~flaskext.uploads.UploadSet`
    :param message: error message

    You can also use the synonym ``file_allowed``.
    """
    套路 __init__(分身, 上传文件集, 消息=空):
        super().__init__(上传文件集, message=消息)

允许文件 = 〇允许文件


类 〇文件大小(FileSize):
    """Validates that the uploaded file is within a minimum and maximum
    file size (set in bytes).

    :param min_size: minimum allowed file size (in bytes). Defaults to 0 bytes.
    :param max_size: maximum allowed file size (in bytes).
    :param message: error message

    You can also use the synonym ``file_size``.
    """

    套路 __init__(分身, 最大, 最小=0, 消息=None):
        super().__init__(最大, min_size=最小, message=消息)

文件大小 = 〇文件大小
