class Text2Pdf:
    @staticmethod
    def get_default_model():
        from sparkocr.transformers import TextToPdf
        return TextToPdf() \
            .setInputCol("positions") \
            .setInputImage("image") \
            .setOutputCol("pdf")
