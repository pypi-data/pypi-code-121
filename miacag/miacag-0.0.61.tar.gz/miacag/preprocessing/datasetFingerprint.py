import numpy as np
import pandas as pd
from ast import literal_eval
#from nnunet.network_architecture.generic_UNet import Generic_UNet
from utils.generic_unet import Generic_UNet
from copy import deepcopy
import argparse
import os
import json
import nibabel as nib


def get_pool_and_conv_props(spacing, patch_size, min_feature_map_size, max_numpool):
    """

    :param spacing:
    :param patch_size:
    :param min_feature_map_size: min edge length of feature maps in bottleneck
    :return:
    """
    dim = len(spacing)

    current_spacing = deepcopy(list(spacing))
    current_size = deepcopy(list(patch_size))

    pool_op_kernel_sizes = []
    conv_kernel_sizes = []

    num_pool_per_axis = [0] * dim

    while True:
        # This is a problem because sometimes we have spacing 20, 50, 50 and we want to still keep pooling.
        # Here we would stop however. This is not what we want! Fixed in get_pool_and_conv_propsv2
        min_spacing = min(current_spacing)
        valid_axes_for_pool = [i for i in range(dim) if current_spacing[i] / min_spacing < 2]
        axes = []
        for a in range(dim):
            my_spacing = current_spacing[a]
            partners = [i for i in range(dim) if current_spacing[i] / my_spacing < 2 and my_spacing / current_spacing[i] < 2]
            if len(partners) > len(axes):
                axes = partners
        conv_kernel_size = [3 if i in axes else 1 for i in range(dim)]

        # exclude axes that we cannot pool further because of min_feature_map_size constraint
        #before = len(valid_axes_for_pool)
        valid_axes_for_pool = [i for i in valid_axes_for_pool if current_size[i] >= 2*min_feature_map_size]
        #after = len(valid_axes_for_pool)
        #if after == 1 and before > 1:
        #    break

        valid_axes_for_pool = [i for i in valid_axes_for_pool if num_pool_per_axis[i] < max_numpool]

        if len(valid_axes_for_pool) == 0:
            break

        #print(current_spacing, current_size)

        other_axes = [i for i in range(dim) if i not in valid_axes_for_pool]

        pool_kernel_sizes = [0] * dim
        for v in valid_axes_for_pool:
            pool_kernel_sizes[v] = 2
            num_pool_per_axis[v] += 1
            current_spacing[v] *= 2
            current_size[v] = np.ceil(current_size[v] / 2)
        for nv in other_axes:
            pool_kernel_sizes[nv] = 1

        pool_op_kernel_sizes.append(pool_kernel_sizes)
        conv_kernel_sizes.append(conv_kernel_size)
        #print(conv_kernel_sizes)

    must_be_divisible_by = get_shape_must_be_divisible_by(num_pool_per_axis)
    patch_size = pad_shape(patch_size, must_be_divisible_by)

    # we need to add one more conv_kernel_size for the bottleneck. We always use 3x3(x3) conv here
    conv_kernel_sizes.append([3]*dim)
    return num_pool_per_axis, pool_op_kernel_sizes, conv_kernel_sizes, patch_size, must_be_divisible_by


def pad_shape(shape, must_be_divisible_by):
    """
    pads shape so that it is divisibly by must_be_divisible_by
    :param shape:
    :param must_be_divisible_by:
    :return:
    """
    if not isinstance(must_be_divisible_by, (tuple, list, np.ndarray)):
        must_be_divisible_by = [must_be_divisible_by] * len(shape)
    else:
        assert len(must_be_divisible_by) == len(shape)

    new_shp = \
        [shape[i] + must_be_divisible_by[i] - shape[i]
            % must_be_divisible_by[i] for i in range(len(shape))]

    for i in range(len(shape)):
        if shape[i] % must_be_divisible_by[i] == 0:
            new_shp[i] -= must_be_divisible_by[i]
    new_shp = np.array(new_shp).astype(int)
    return new_shp


def get_shape_must_be_divisible_by(net_numpool_per_axis):
    return 2 ** np.array(net_numpool_per_axis)


def convert_string_to_tuple(liste):
    res = []
    for l in liste:
        res.append(literal_eval(l))
    res = np.array(res)
    return res


class datasetFingerprint():
    def __init__(self):
        self.unet_base_num_features = 32
        self.unet_max_numpool = 999
        self.unet_max_num_filters = 320
        self.conv_per_stage = 2
        self.unet_min_batch_size = 2
        self.unet_featuremap_min_edge_length = 4
        self.batch_size_covers_max_percent_of_dataset = 0.05
        self.anisotropy_threshold = 3

    def get_modality(self, df):
        features = [col for col in
                    df.columns.tolist() if col.startswith('mod')]
        return features

    # def get_target_spacing(self, spacings):
    #     target = np.percentile(np.vstack(spacings), 50, 0)
    #     return target

    def get_target_spacing(self, spacings, sizes, pecentile=50):
        target = np.percentile(np.vstack(spacings),
                               pecentile, 0)

        # This should be used to determine the new median shape. The old implementation is not 100% correct.
        # Fixed in 2.4
        # sizes = [np.array(i) / target * np.array(j) for i, j in zip(spacings, sizes)]

        target_size = np.percentile(np.vstack(sizes),
                                    pecentile, 0)
        target_size_mm = np.array(target) * np.array(target_size)
        # we need to identify datasets for which a different target spacing could be beneficial. These datasets have
        # the following properties:
        # - one axis which much lower resolution than the others
        # - the lowres axis has much less voxels than the others
        # - (the size in mm of the lowres axis is also reduced)
        worst_spacing_axis = np.argmax(target)
        other_axes = [i for i in range(len(target)) if i != worst_spacing_axis]
        other_spacings = [target[i] for i in other_axes]
        other_sizes = [target_size[i] for i in other_axes]

        has_aniso_spacing = target[worst_spacing_axis] > \
            (self.anisotropy_threshold * max(other_spacings))
        has_aniso_voxels = target_size[worst_spacing_axis] * \
            self.anisotropy_threshold < min(other_sizes)
        # we don't use the last one for now
        # median_size_in_mm = target[target_size_mm] * \
        # RESAMPLING_SEPARATE_Z_ANISOTROPY_THRESHOLD < max(target_size_mm)

        if has_aniso_spacing and has_aniso_voxels:
            spacings_of_that_axis = np.vstack(spacings)[:, worst_spacing_axis]
            target_spacing_of_that_axis = np.percentile(spacings_of_that_axis,
                                                        10)
            # don't let the spacing of that axis get higher than the other axes
            if target_spacing_of_that_axis < max(other_spacings):
                target_spacing_of_that_axis = max(
                    max(other_spacings), target_spacing_of_that_axis) + 1e-5
            target[worst_spacing_axis] = target_spacing_of_that_axis
        return target

    def get_properties_for_stage(self, current_spacing, original_spacing,
                                 original_shape, num_cases,
                                 num_modalities, num_classes):
        """
        ExperimentPlanner configures pooling so that we pool late. Meaning that if the number of pooling per axis is
        (2, 3, 3), then the first pooling operation will always pool axes 1 and 2 and not 0, irrespective of spacing.
        This can cause a larger memory footprint, so it can be beneficial to revise this.

        Here we are pooling based on the spacing of the data.

        """
        new_median_shape = np.round(
            original_spacing / current_spacing * original_shape).astype(int)
        dataset_num_voxels = np.prod(new_median_shape) * num_cases

        # the next line is what we had before as a default.
        # The patch size had the same aspect ratio
        # the median shape of a patient. We swapped t
        # input_patch_size = new_median_shape

        # compute how many voxels are one mm
        input_patch_size = 1 / np.array(current_spacing)

        # normalize voxels per mm
        input_patch_size /= input_patch_size.mean()

        # create an isotropic patch of size 512x512x512mm
        # # to get a starting value
        input_patch_size *= 1 / min(input_patch_size) * 512
        input_patch_size = np.round(input_patch_size).astype(int)

        # clip it to the median shape of the dataset
        # because patches larger then that make not much sense
        input_patch_size = [min(i, j) for i, j in zip(
            input_patch_size, new_median_shape)]

        network_num_pool_per_axis, pool_op_kernel_sizes, \
            conv_kernel_sizes, new_shp, shape_must_be_divisible_by = \
            get_pool_and_conv_props(
                current_spacing, input_patch_size,
                self.unet_base_num_features,
                self.unet_max_numpool)

        # we compute as if we were using only 30 feature maps.
        # We can do that because fp16 training is the standard
        # now. That frees up some space.
        # The decision to go with 32 is solely due
        # to the speedup we get (non-multiples
        # of 8 are not supported in nvidia amp)
        ref = Generic_UNet.use_this_for_batch_size_computation_3D * \
            self.unet_base_num_features / \
            Generic_UNet.BASE_NUM_FEATURES_3D
        here = Generic_UNet.compute_approx_vram_consumption(
            new_shp, network_num_pool_per_axis,
            self.unet_base_num_features,
            self.unet_max_num_filters, num_modalities,
            num_classes,
            pool_op_kernel_sizes, conv_per_stage=self.conv_per_stage)
        while here > ref:
            axis_to_be_reduced = np.argsort(new_shp / new_median_shape)[-1]

            tmp = deepcopy(new_shp)
            tmp[axis_to_be_reduced] -= \
                shape_must_be_divisible_by[axis_to_be_reduced]
            _, _, _, _, shape_must_be_divisible_by_new = \
                get_pool_and_conv_props(current_spacing, tmp,
                                        self.unet_featuremap_min_edge_length,
                                        self.unet_max_numpool,
                                        )
            new_shp[axis_to_be_reduced] -= shape_must_be_divisible_by_new[axis_to_be_reduced]

            # we have to recompute numpool now:
            network_num_pool_per_axis, pool_op_kernel_sizes, \
                conv_kernel_sizes, new_shp, shape_must_be_divisible_by = \
                get_pool_and_conv_props(
                    current_spacing, new_shp,
                    self.unet_featuremap_min_edge_length,
                    self.unet_max_numpool,
                    )

            here = Generic_UNet.compute_approx_vram_consumption(
                new_shp, network_num_pool_per_axis,
                self.unet_base_num_features,
                self.unet_max_num_filters, num_modalities,
                num_classes, pool_op_kernel_sizes,
                conv_per_stage=self.conv_per_stage)

        input_patch_size = new_shp

        # This is what wirks with 128**3
        batch_size = Generic_UNet.DEFAULT_BATCH_SIZE_3D
        batch_size = int(np.floor(max(ref / here, 1) * batch_size))

        # check if batch size is too large
        max_batch_size = np.round(
            self.batch_size_covers_max_percent_of_dataset
            * dataset_num_voxels /
            np.prod(input_patch_size, dtype=np.int64)).astype(int)
        max_batch_size = max(max_batch_size, self.unet_min_batch_size)
        batch_size = min(batch_size, max_batch_size)

        do_dummy_2D_data_aug = (max(input_patch_size) / input_patch_size[
            0]) > self.anisotropy_threshold

        plan = {
            'batch_size': batch_size,
            'num_pool_per_axis': network_num_pool_per_axis,
            'patch_size': input_patch_size.tolist(),
            'median_patient_size_in_voxels': new_median_shape.tolist(),
            'current_spacing': current_spacing.tolist(),
            'original_spacing': original_spacing.tolist(),
            'do_dummy_2D_data_aug': str(do_dummy_2D_data_aug),
            'pool_op_kernel_sizes': pool_op_kernel_sizes,
            'conv_kernel_sizes': conv_kernel_sizes,
        }
        return plan

    def plan_experiment(self, ):
        spacings = self.dataset_properties['all_spacings']
        sizes = self.dataset_properties['all_sizes']

        all_classes = self.dataset_properties['all_classes']
        modalities = self.dataset_properties['modalities']
        num_modalities = len(list(modalities.keys()))

        target_spacing = self.get_target_spacing()
        new_shapes = [np.array(i) / target_spacing * np.array(j) for i, j in zip(spacings, sizes)]

        max_spacing_axis = np.argmax(target_spacing)
        remaining_axes = [i for i in list(range(3)) if i != max_spacing_axis]
        self.transpose_forward = [max_spacing_axis] + remaining_axes
        self.transpose_backward = [np.argwhere(np.array(self.transpose_forward) == i)[0][0] for i in range(3)]

        # we base our calculations on the median shape of the datasets
        median_shape = np.median(np.vstack(new_shapes), 0)
        print("the median shape of the dataset is ", median_shape)

        max_shape = np.max(np.vstack(new_shapes), 0)
        print("the max shape in the dataset is ", max_shape)
        min_shape = np.min(np.vstack(new_shapes), 0)
        print("the min shape in the dataset is ", min_shape)

        print("we don't want feature maps smaller than ", self.unet_featuremap_min_edge_length, " in the bottleneck")

        # how many stages will the image pyramid have?
        self.plans_per_stage = list()

        target_spacing_transposed = np.array(target_spacing)[self.transpose_forward]
        median_shape_transposed = np.array(median_shape)[self.transpose_forward]
        print("the transposed median shape of the dataset is ", median_shape_transposed)

        print("generating configuration for 3d_fullres")
        self.plans_per_stage.append(self.get_properties_for_stage(target_spacing_transposed, target_spacing_transposed,
                                                                  median_shape_transposed,
                                                                  len(self.list_of_cropped_npz_files),
                                                                  num_modalities, len(all_classes) + 1))

        # thanks Zakiyi (https://github.com/MIC-DKFZ/nnUNet/issues/61) for spotting this bug :-)
        # if np.prod(self.plans_per_stage[-1]['median_patient_size_in_voxels'], dtype=np.int64) / \
        #        architecture_input_voxels < HOW_MUCH_OF_A_PATIENT_MUST_THE_NETWORK_SEE_AT_STAGE0:
        architecture_input_voxels_here = np.prod(self.plans_per_stage[-1]['patch_size'], dtype=np.int64)
        if np.prod(self.plans_per_stage[-1]['median_patient_size_in_voxels'], dtype=np.int64) / \
                architecture_input_voxels_here < self.how_much_of_a_patient_must_the_network_see_at_stage0:
            more = False
        else:
            more = True

        if more:
            print("generating configuration for 3d_lowres")
            # if we are doing more than one stage then we want the lowest stage to have exactly
            # HOW_MUCH_OF_A_PATIENT_MUST_THE_NETWORK_SEE_AT_STAGE0 (this is 4 by default so the number of voxels in the
            # median shape of the lowest stage must be 4 times as much as the network can process at once (128x128x128 by
            # default). Problem is that we are downsampling higher resolution axes before we start downsampling the
            # out-of-plane axis. We could probably/maybe do this analytically but I am lazy, so here
            # we do it the dumb way

            lowres_stage_spacing = deepcopy(target_spacing)
            num_voxels = np.prod(median_shape, dtype=np.int64)
            while num_voxels > self.how_much_of_a_patient_must_the_network_see_at_stage0 * architecture_input_voxels_here:
                max_spacing = max(lowres_stage_spacing)
                if np.any((max_spacing / lowres_stage_spacing) > 2):
                    lowres_stage_spacing[(max_spacing / lowres_stage_spacing) > 2] \
                        *= 1.01
                else:
                    lowres_stage_spacing *= 1.01
                num_voxels = np.prod(target_spacing / lowres_stage_spacing * median_shape, dtype=np.int64)

                lowres_stage_spacing_transposed = np.array(lowres_stage_spacing)[self.transpose_forward]
                new = self.get_properties_for_stage(lowres_stage_spacing_transposed, target_spacing_transposed,
                                                    median_shape_transposed,
                                                    len(self.list_of_cropped_npz_files),
                                                    num_modalities, len(all_classes) + 1)
                architecture_input_voxels_here = np.prod(new['patch_size'], dtype=np.int64)
            if 2 * np.prod(new['median_patient_size_in_voxels'], dtype=np.int64) < np.prod(
                    self.plans_per_stage[0]['median_patient_size_in_voxels'], dtype=np.int64):
                self.plans_per_stage.append(new)

        self.plans_per_stage = self.plans_per_stage[::-1]
        self.plans_per_stage = {i: self.plans_per_stage[i] for i in range(len(self.plans_per_stage))}  # convert to dict

        print(self.plans_per_stage)
        print("transpose forward", self.transpose_forward)
        print("transpose backward", self.transpose_backward)

        normalization_schemes = self.determine_normalization_scheme()
        only_keep_largest_connected_component, min_size_per_class, min_region_size_per_class = None, None, None
        # removed training data based postprocessing. This is deprecated

        # these are independent of the stage
        plans = {'num_stages': len(list(self.plans_per_stage.keys())), 'num_modalities': num_modalities,
                 'modalities': modalities, 'normalization_schemes': normalization_schemes,
                 'dataset_properties': self.dataset_properties, 'list_of_npz_files': self.list_of_cropped_npz_files,
                 'original_spacings': spacings, 'original_sizes': sizes,
                 'preprocessed_data_folder': self.preprocessed_output_folder, 'num_classes': len(all_classes),
                 'all_classes': all_classes, 'base_num_features': self.unet_base_num_features,
                 'use_mask_for_norm': use_nonzero_mask_for_normalization,
                 'keep_only_largest_region': only_keep_largest_connected_component,
                 'min_region_size_per_class': min_region_size_per_class, 'min_size_per_class': min_size_per_class,
                 'transpose_forward': self.transpose_forward, 'transpose_backward': self.transpose_backward,
                 'data_identifier': self.data_identifier, 'plans_per_stage': self.plans_per_stage,
                 'preprocessor_name': self.preprocessor_name,
                 'conv_per_stage': self.conv_per_stage,
                 }


    def getMedianShape(self, target_spacing, spacings, sizes):
        new_shapes = [np.array(i) / target_spacing * np.array(j) for i, j in zip(spacings, sizes)]
        median_shape = np.median(np.vstack(new_shapes), 0)
        return median_shape

def getSpacings(image_path):
    img = nib.load(example_filename)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv_path",
                        default="/media/gandalf/AE3416073415D2E7/CHAOS_pancreas_MRI_nifty/Task038_CHAOS_Task_3_5_Variant2/train.csv",
                        type=str,
                        help="train csv path")
    parser.add_argument("--val_csv_path",
                        default="/media/gandalf/AE3416073415D2E7/CHAOS_pancreas_MRI_nifty/Task038_CHAOS_Task_3_5_Variant2/val.csv",
                        type=str,
                        help="val csv path")
    parser.add_argument("--outpath",
                        default="segmentation/CHAOS",
                        type=str,
                        help="outpath")
    parser.add_argument("--classes",
                        default=5,
                        type=int,
                        help="number of classes")
    args = parser.parse_args()
    train_csv = args.train_csv_path
    val_csv = args.val_csv_path
    outpath = args.outpath
    classes = args.classes

    train_df = pd.read_csv(train_csv, dtype=str)
    val_df = pd.read_csv(val_csv, dtype=str)
    df = pd.concat([train_df, val_df])
    datasetF = datasetFingerprint()

    spacing_np = convert_string_to_tuple(df['spacings'].tolist())
    sizes_np = convert_string_to_tuple(df['sizes'].tolist())
    target_spacing = datasetF.get_target_spacing(spacing_np, sizes_np)
    median_shape = datasetF.getMedianShape(target_spacing,
                                           spacing_np,
                                           sizes_np)
    modalities = datasetF.get_modality(df)
    stages = datasetF.get_properties_for_stage(target_spacing,
                                               target_spacing,
                                               median_shape,
                                               len(df),
                                               num_modalities=len(modalities),
                                               num_classes=classes)
    json_out_path = os.path.join('configs', outpath,
                                 'dataset_fingerprint.json')
    with open(json_out_path, 'w') as file:
        file.write(json.dumps(stages,
                   sort_keys=True, indent=4,
                   separators=(',', ': ')))
