from typing import Dict, List, Union
from pathlib import Path
import climetlab as cml
import rechunker as rc
import zarr
from zarr.errors import ContainsArrayError
import shutil
import xarray as xr
"""
The adapter should configure where, what and how the data should be saved.
The scopes are:
1. Save and cache files in a non default directory with user selected names
2. On top of (1) prepare data for the viewer (slice vs series orientation)
"""



class Adapter:

    def __init__(self, dataset: cml.Dataset, output_folder: str, output_name_prefix: str, key_mapping: Dict[str, str] = None):
        self.dataset = dataset
        self.output_folder = Path(output_folder)
        self.output_name_prefix = output_name_prefix
        self.output_name = "-".join([self.dataset.name,self.output_name_prefix])
        self.output_path = None
        

        if self.dataset.output_names is None:
            self.output_path = [self.output_folder / self.output_name]
        else:
            self.output_path = []
            for fn in self.dataset.output_names:
                file_name = "_".join([self.output_name, fn])
                self.output_path.append(self.output_folder / file_name)



    def to_netcdf(self, ret=False): # all individual save or merge everything and then save
        paths = []    
        if len(self.output_path) < 2:
            ds = self.dataset.to_xarray()
            p = self.output_path[0].with_suffix('.nc')
            paths.append(p)
            if not p.exists():
                ds.to_netcdf(p)
        else:
            for i,src in enumerate(self.dataset.source.sources):
                ds = src.to_xarray()
                p = self.output_path[i].with_suffix('.nc')
                paths.append(p)
                if not p.exists():
                    ds.to_netcdf(p)

        if ret:
            return paths

    def to_zarr(self, rechunk: bool = False, target_chunks: Dict[str, Union[Dict[str, int], None]] = {}, max_mem: str = '2M', temp_store = 'temp.zarr'):
        #ds = self.dataset.to_xarray()
        paths = self.to_netcdf(ret=True)
                
        out_name = self.output_folder / self.output_name
        out_name_fmt = out_name.with_suffix('.zarr')
        out_target_name = self.output_folder / "_".join(["rc",self.output_name])
        temp_store = self.output_folder / temp_store

        
        if len(self.output_path) < 2:
            dsnc = xr.open_dataset(paths[0])
        else:
            dsnc = xr.open_mfdataset(paths)

        
        if not out_name_fmt.exists():
            dsnc.to_zarr(out_name_fmt, mode ="w")
        
        if temp_store.exists():
            shutil.rmtree(temp_store)

        if rechunk:
            ds = zarr.open(out_name_fmt)
            try: 
                ret = rc.rechunk(ds, target_chunks, max_mem, out_target_name, temp_store=temp_store)
                ret.execute()
            except ContainsArrayError:
                print("Cannot write on non-empty zarr")
            shutil.rmtree(temp_store)
        else:
            ds.to_zarr(out_name_fmt, mode ="w")


    
