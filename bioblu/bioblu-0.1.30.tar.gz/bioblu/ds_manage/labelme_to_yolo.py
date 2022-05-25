#!/usr/bin/env python3

from bioblu.ds_manage import ds_convert


if __name__ == "__main__":
    # labelme_output = '/media/findux/HDD/Malta_II/surveys/2022-01-28_Gnejna_beach/Test_Gnejna_bay 28-01-2022/RGB images/5m altitude/Gnejna_tiles_2022-02-08/'
    labelme_output = "/media/findux/DATA/Documents/Malta_II/surveys/2022-01-28_Gnejna_beach/Test_Gnejna_bay 28-01-2022/RGB images/5m altitude/with_duplicates/"
    yolo_target_dir = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates"
    annotations_df = ds_convert.create_yolo_annotations(labelme_output)
    ds_convert.create_yolo_dataset(labelme_output, yolo_target_dir, train_val_test=(0.6, 0.2, 0.2))