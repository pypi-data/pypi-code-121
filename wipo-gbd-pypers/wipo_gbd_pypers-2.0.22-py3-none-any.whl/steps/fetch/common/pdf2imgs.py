import os
from pypers.steps.base.step_generic import EmptyStep


class PDF2IMGs(EmptyStep):

    spec = {
        "version": "2.0",
        "descr": [
            "converts every page of a pdf document to a jpg image"
        ],
        "args":
        {
            "inputs": [
                {
                    "name": "input_data",
                    "descr": "input structured data",
                    "iterable": True
                },
                {
                    "name": "input_dir",
                    "descr": "the extraction dir",
                    "iterable": True
                }
            ],
            'outputs': [
                {
                    'name': 'output_data',
                    'descr': 'output processed images'
                }
            ]
        }
    }

    def process(self):
        # nothing to do here. exit.
        if not len(self.input_data):
            return

        # variables to find images in pdf
        startmark = b"\xff\xd8"
        startfix = 0
        endmark = b"\xff\xd9"
        endfix = 2

        for item in self.input_data:
            try:
                pdf_file = item.pop('pdf')
            except Exception as e:
                continue

            pdf_file = os.path.realpath(os.path.join(self.input_dir, pdf_file))

            if not os.path.exists(pdf_file):
                continue

            img_base = item.get('appnum')
            img_path = os.path.dirname(pdf_file)

            item['img'] = []

            # open a file reader on pdf
            with open(pdf_file, 'rb') as f:
                pdf = f.read()
                # reset counters for pdf reader
                i = njpg = 0
                while True:
                    istream = pdf.find(b'stream', i)
                    if istream < 0:
                        break
                    istart = pdf.find(startmark, istream, istream+20)

                    if istart < 0:
                        i = istream+20
                        continue

                    iend = pdf.find(b'endstream', istart)
                    if iend < 0:
                        self.logger.error(
                            'ERROR: corrupt pdf file: %s' % item['pdf_uri'])
                        break
                    iend = pdf.find(endmark, iend-20)
                    # no end of jpg, then take the end of pdf
                    if iend < 0:
                        iend = pdf.find(b"endstream", istart)

                    istart += startfix
                    iend += endfix
                    njpg += 1

                    jpg = pdf[istart:iend]

                    img_file = os.path.join(img_path, '%s.%d.jpg' % (
                        img_base, njpg))
                    self.logger.info(
                        '  %d:%s' % (njpg, '%s.%d.jpg' % (img_base, njpg)))
                    with open(img_file, 'wb') as jpgfile:
                        jpgfile.write(jpg)
                        jpgfile.close()
                    item['img'].append(img_file)
                    i = iend
            os.remove(pdf_file)
        self.output_data = [self.input_data]
