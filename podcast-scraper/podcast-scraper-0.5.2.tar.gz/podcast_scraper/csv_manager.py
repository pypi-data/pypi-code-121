from pathlib import Path


class CsvManager:

    limit = -1

    def with_csv(self, csv_path):
        import pandas as pd

        self.dataset = pd.read_csv(Path(csv_path))
        return self

    def with_output(self, dir):
        self.output_dir = Path(dir)
        return self

    def with_limit(self, limit):
        self.limit = limit
        return self

    def download(self):
        import requests

        counter = 0
        for row in self.dataset.itertuples():
            if row.file != row.file:  # no file / is nan
                continue
            if self.limit == -1 or counter < self.limit:
                dir_file = self.output_dir / row.file
                if dir_file.exists():
                    print(dir_file, "already exist", "not downloading")
                    continue
                print(dir_file, "not exist", " downloading")
                podcast = requests.get(row.url)
                with open(dir_file, "wb") as wt:
                    wt.write(podcast.content)
            counter += 1
        return self

    def replace_tags(self):
        counter = 0
        for row in self.dataset.itertuples():
            if row.file != row.file:  # no file / is nan
                continue
            if self.limit == -1 or counter < self.limit:
                dir_file = self.output_dir / row.file
                if not dir_file.exists():
                    print(dir_file, "does not exist")
                    continue
                print(dir_file, "exist")
                st_size = dir_file.stat().st_size
                if st_size <= 1 * 1000 * 1000:
                    print(st_size, "too small podcast, skipping")
                    continue
                import music_tag

                ptag = music_tag.load_file(dir_file)
                ptag["title"] = row.title
                ptag["artist"] = row.artist
                ptag["album"] = row.album
                ptag["year"] = row.date
                ptag["comment"] = row.date
                ptag.save()
            counter += 1
        return self
