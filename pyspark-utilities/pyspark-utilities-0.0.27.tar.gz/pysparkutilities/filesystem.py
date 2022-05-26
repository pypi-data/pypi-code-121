from .datastorage import DataStorage
from .utils import get_dataset_property

class Filesystem(DataStorage):

    # overriding abstract method
    def load_dataset(self, name, read_all=False, input_dest='', header=True):

        if input_dest == '':
            input_dataset = get_dataset_property(name)
        else:
            input_dataset = input_dest
        
        delimiter = get_dataset_property(name, "delimiter") if get_dataset_property(name, "delimiter") is not None else ","
        input_file_format = get_dataset_property(name, "inputFileFormat") if get_dataset_property(name, "inputFileFormat") is not None else "csv"
        
        df = self.spark.read.load(input_dataset, format=input_file_format, sep=delimiter, inferSchema=True, header=header, error_bad_lines=False)

        if read_all == False:
            input_cols = get_dataset_property(name, "input-columns")
            if input_cols is not None and input_cols != "*":
                df = df.select(self.args[input_cols].split(delimiter))

        return df

    # overriding abstract method
    def save_dataset(self, name, df, output_dest):

        if output_dest == '':
            output_dataset = get_dataset_property(name)
        else:
            output_dataset = output_dest
        delimiter = get_dataset_property(name, "delimiter") if get_dataset_property(name, "delimiter") is not None else ","
        output_file_format = get_dataset_property(name, "outputFileFormat") if get_dataset_property(name, "outputFileFormat") is not None else "csv"

        if "save_dataset_with_pandas" in self.args:

            df.toPandas().to_csv(output_dataset, sep=delimiter, index=False)

        else:

            df.write.options(delimiter=delimiter).\
                mode('overwrite').\
                option("header", True).\
                save(output_dataset, format=output_file_format)
