import pandas
def to_tsv(xlsx_file):
    data_frame=pandas.read_excel(xlsx_file,index_col=None)
    # Replace all columns having spaces with underscores
    data_frame.columns = [c.replace(' ', '_') for c in data_frame.columns]

    # Replace all fields having line breaks with space
    data_frame = data_frame.replace('\n', ' ', regex=True)

    # Write dataframe into csv
    data_frame.to_csv(f'{xlsx_file.replace(".xlsx",".tsv")}', sep='\t', encoding='utf-8', index=False, line_terminator='\r\n')
