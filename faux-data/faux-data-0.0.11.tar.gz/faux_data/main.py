from .template import Template

## Testing stuff
if __name__ == '__main__':
    t1 = """
    tables:
      - name: mytable
        rows: 10
        columns:
          - name: mycol
            column_type: Random
            min: 3
            max: 4

          - name: myothercol
            column_type: Selection
            values:
              - a
              - b

          - col: col2 Fixed Int 2
    """

    r = Template.from_string(t1)

    rf = Template.from_file(r"tests/example_files/t1.yaml")

    rf.generate()

    print(rf)
    print(r.tables[0].generate())

    # print(r.tables[0].generate())

    # print(r.tables[0].df)
    #print(list((dataclasses.fields(c) for c in Column.__subclasses__())))
