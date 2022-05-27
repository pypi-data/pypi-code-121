class VisualDocClassifier:
    @staticmethod
    def get_default_model():
        from sparkocr.transformers import VisualDocumentClassifier
        return VisualDocumentClassifier() \
            .setMaxSentenceLength(128) \
            .setInputCol("hocr") \
            .setLabelCol("label") \
            .setConfidenceCol("conf")

    @staticmethod
    def get_pretrained_model(name, language, bucket="clinical/ocr"):
        from sparkocr.transformers import VisualDocumentClassifier
        return VisualDocumentClassifier() \
            .pretrained(name, language, bucket) \
            .setMaxSentenceLength(128) \
            .setInputCol("hocr") \
            .setLabelCol("label") \
            .setConfidenceCol("conf")
