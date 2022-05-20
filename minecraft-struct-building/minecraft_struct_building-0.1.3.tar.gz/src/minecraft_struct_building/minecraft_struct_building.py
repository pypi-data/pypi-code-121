"""
マイクラの建造物を保存したcsvデータから建造物を作る
"""

import argparse
import mcpi.minecraft as minecraft
import pandas as pd
import csv
import time
import copy


class Struct:
    def __init__(self):
        self.mc = minecraft.Minecraft.create()
        self.blocks = None

    def load_data(self, path):
        """
        csvファイルから建造物のデータをロードする
        :param path: csvのパス
        :return:
        """
        with open(path) as f:
            reader = csv.reader(f)
            blocks = [row for row in reader][1:]
        self.blocks = blocks
        self._type_convert_to_int()

    def load_data_by_list(self, blocks):
        """
        リストからデータをロードする
        :param blocks: ブロックデータのリスト
        :return:
        """
        self.blocks = blocks

    def size(self):
        """
        建造物のサイズを計測する
        :return x_size, y_size, z_size: x,y,zをれぞれの建造物のサイズ
        """
        x = [block[0] for block in self.blocks]
        y = [block[1] for block in self.blocks]
        z = [block[2] for block in self.blocks]

        x_size = max(x) - min(x) + 1
        y_size = max(y) - min(y) + 1
        z_size = max(z) - min(z) + 1

        return x_size, y_size, z_size


    def struct_building(self, x, y, z):
        """
        csvファイルから建造物の構築をする
        :param x: 建造物の角 x座標
        :param y: 建造物の角 y座標
        :param z: 建造物の角 z座標
        :return:
        """
        for block in self.blocks:
            self.mc.setBlock(
                x + block[0], y + block[1], z + block[2], block[3], block[4]
            )

    def struct_slice_building(self, x, y, z, sleep_time=1, slice_direction="y"):
        """
        csvファイルから建造物の構築をする y値が小さいところから順番に作っていく
        :param x: 建造物の角 x座標
        :param y: 建造物の角 y座標
        :param z: 建造物の角 z座標
        :param sleep_time: 1段ずつ作るときの待ち時間
        :param slice_direction: 1段ずつ作っていく方向
        :return:
        """
        blocks = pd.DataFrame(self.blocks, columns=["x", "y", "z", "id", "data"])
        labels = blocks.drop_duplicates(subset=slice_direction)
        for y_ in labels[slice_direction]:
            slice_blocks = blocks[blocks[slice_direction] == y_]
            for block in slice_blocks.itertuples():
                self.mc.setBlock(
                    x + block.x, y + block.y, z + block.z, block.id, block.data
                )
            time.sleep(sleep_time)

    def exchange_block(self, replace_blocks, new_blocks, replace=False):
        """
        構築するブロックをいれかえる
        :param replace_blocks: 置き換える元のブロックid,dataのリスト
        :param new_blocks: 置き換える先のブロックid,dataのリスト
        :param replace:クラス内のデータを書き換えるかどうか デフォルトはFalse
        :return: ブロックid,データ書き換え後のブロックリスト
        """
        change_blocks = copy.copy(self.blocks)

        for block in change_blocks:
            for replace_block, new_block in zip(replace_blocks, new_blocks):
                if block[3] == replace_block[0] and block[4] == replace_block[1]:
                    block[3] = new_block[0]
                    block[4] = new_block[1]
                    continue

        if replace is True:
            self.blocks = change_blocks

        elif replace is False:
            return change_blocks

    def delete_building(self, x, y, z):
        """
        csvファイルから建造物の構築をする
        :param x: 建造物の角 x座標
        :param y: 建造物の角 y座標
        :param z: 建造物の角 z座標
        :return:
        """
        for block in self.blocks:
            self.mc.setBlock(x + block[0], y + block[1], z + block[2], 0, 0)

    def _type_convert_to_int(self):
        """
        csvで読み込んだブロックデータをstr型からint型に変更する
        :return:
        """
        int_blocks = []
        for block in self.blocks:
            int_blocks.append([int(b) for b in block])

        self.blocks = int_blocks


def main():
    """
    コマンドラインで動くときの関数
    :return:
    """

    def replace_list_convert_to_int(blocks):
        blocks = blocks[1:-1].split("[")[1:]
        int_blocks = []
        for block in blocks:
            block = block.replace("]", "").split(",")
            int_blocks.append([int(block[0]), int(block[1])])
        return int_blocks

    parser = argparse.ArgumentParser()
    parser.add_argument("x", help="建物の角のx座標", type=int)
    parser.add_argument("y", help="建物の角のy座標", type=int)
    parser.add_argument("z", help="建物の角のz座標", type=int)
    parser.add_argument("csv_path", help="読み込むcsvのパス先")
    parser.add_argument("-r", "--replace_blocks", help="置き換え元のブロック")
    parser.add_argument("-n", "--new_blocks", help="置き換え先のブロック")
    parser.add_argument(
        "-s", "--slice_struct", default=False, help="端から順番に置くかどうか", type=bool
    )
    parser.add_argument(
        "-sd", "--slice_direction", default="y", help="slice_structの方向を決める x,y,z"
    )
    parser.add_argument(
        "-st", "--sleep_time", default=1, help="slice_structを指定したときの1段ごとの待ち時間、秒"
    )
    args = parser.parse_args()

    struct = Struct()
    struct.load_data(args.csv_path)
    if args.replace_blocks is not None and args.new_blocks is not None:
        args.replace_blocks = replace_list_convert_to_int(args.replace_blocks)
        args.new_blocks = replace_list_convert_to_int(args.new_blocks)
        struct.exchange_block(
            replace_blocks=args.replace_blocks, new_blocks=args.new_blocks, replace=True
        )

    if args.slice_struct is True:
        struct.struct_slice_building(
            args.x,
            args.y,
            args.z,
            sleep_time=args.sleep_time,
            slice_direction=args.slice_direction,
        )
    else:
        struct.struct_building(args.x, args.y, args.z)


if __name__ == "__main__":
    main()
