try:
    from read_lif.read_lif import Reader, Serie
except:
    exit("install read_lif module: pip install read-lif")
import numpy as np
import warnings
import sys


class LIFReader(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getSeries(self):
        if not hasattr(self, '__series'):
            self.__series = [
                LIFSerie(s.root, self.f, self.offsets[i]) for i, s in enumerate(self.getSeriesHeaders())
            ]
        return self.__series


class LIFSerie(Serie):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getStack(self, channels=None):
        if channels is None:
            channelInfos = self.getChannels()
            channels = [int(c.getAttribute("ChannelTag")) for c in channelInfos]
        elif type(channels) is int:
            channels = [channels]
        elif type(channels) is tuple:
            channels = list(channels)

        channelStacks = []
        for i, channel in enumerate(channels):
            print("... Loading channel {}/{}".format(i+1, len(channels)))
            channelStacks.append(self.__getStackChannel(channel))

        return np.stack(channelStacks, axis=2)

    def __getStackChannel(self, channel=0, T=0, dtype=np.uint8):
        """ Renamed custom version of getFrame """
        zcyx = []
        zSize = self.getBoxShape()[-1]
        for z in range(zSize):
            progressBar(z, zSize-1)
            cyx = []
            self.f.seek(self.getOffset(**dict({'T': T, 'Z': z})) + self.getChannelOffset(channel))
            yx = np.fromfile(self.f, dtype=dtype, count=int(self.getNbPixelsPerSlice()))
            yx = yx.reshape(self.get2DShape())
            cyx.append(yx)
            zcyx.append(cyx)
        print('\n')  # Leave progress bar inline update
        zcyx = np.array(zcyx)
        xzcy = np.moveaxis(zcyx, -1, 0)
        xyzc = np.moveaxis(xzcy, -1, 1)
        return xyzc[:, :, :, 0]

    def getMetadata(self):
        """
        Overwrites original getMetadata to allow 2D Series
        """
        boxShape = self.getBoxShape()
        if len(boxShape) == 2:
            boxShape.append(None)
        nbx, nby, nbz = boxShape
        setting_records = self.root.getElementsByTagName('ScannerSettingRecord')
        dimension_descriptions = self.root.getElementsByTagName('DimensionDescription')
        if setting_records:
            # ScannerSettingRecord only available for some lif files!
            psx = self.getVoxelSize(1)  # m ---> µm
            psy = self.getVoxelSize(2)  # m ---> µm
            psz = self.getVoxelSize(3)  # m ---> µm
            unit_x = [s.getAttribute('Unit') for s in setting_records if s.getAttribute('Identifier') == 'dblVoxelX'][0]
            unit_y = [s.getAttribute('Unit') for s in setting_records if s.getAttribute('Identifier') == 'dblVoxelY'][0]
            unit_z = [s.getAttribute('Unit') for s in setting_records if s.getAttribute('Identifier') == 'dblVoxelZ'][0]
            units = [unit_x, unit_y, unit_z]
        elif dimension_descriptions:
            # Use DimensionDescription to get voxel information
            length_x = float(
                [d.getAttribute('Length') for d in dimension_descriptions if d.getAttribute('DimID') == '1'][0])
            length_y = float(
                [d.getAttribute('Length') for d in dimension_descriptions if d.getAttribute('DimID') == '2'][0])
            if nbz is None:
                length_z = None
            else:
                length_z = float(
                    [d.getAttribute('Length') for d in dimension_descriptions if d.getAttribute('DimID') == '3'][0])
            number_x = float(
                [d.getAttribute('NumberOfElements') for d in dimension_descriptions if d.getAttribute('DimID') == '1'][
                    0])
            number_y = float(
                [d.getAttribute('NumberOfElements') for d in dimension_descriptions if d.getAttribute('DimID') == '2'][
                    0])
            if nbz is None:
                number_z = None
            else:
                number_z = float(
                [d.getAttribute('NumberOfElements') for d in dimension_descriptions if d.getAttribute('DimID') == '3'][
                    0])
            psx = length_x / number_x
            psy = length_y / number_y
            if nbz is None:
                psz = None
            else:
                psz = length_z / number_z
            units = [s.getAttribute('Unit') for s in dimension_descriptions]
        else:
            raise RuntimeError("Can't find voxel information in the lif file!")

        if len(set(units)) == 1 and 'm' in units:
            factor = 1e6
            unit = 'um'
        else:
            warnings.warn('unit is not meter, check the unit of voxel size')
            factor = 1
            unit = ", ".join(units)

        psx = psx * factor  # m ---> µm
        psy = psy * factor  # m ---> µm
        if nbz is not None:
            psz = psz * factor  # m ---> µm

        return {
            'voxel_size_x': psx,
            'voxel_size_y': psy,
            'voxel_size_z': psz,
            'voxel_size_unit': unit,
            'voxel_number_x': nbx,
            'voxel_number_y': nby,
            'voxel_number_z': nbz,
            'channel_number': len(self.getChannels()),
            'frame_number': self.getNbFrames(),
        }


def progressBar(value, endvalue, bar_length=20):

        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\r   [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()
