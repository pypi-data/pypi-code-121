# Copyright (c) 2017-2022, NVIDIA CORPORATION.  All rights reserved.

"""Script to convert onnx model to keras and save weights/acrhictures in EFF."""

import os
import sys
import argparse
import keras
import onnx
import logging

import tao_byom
from tao_byom.layers.layers import AVAILABLE_CONVERTERS
from tao_byom.converter import tao_byom_converter
from tao_byom.utils.model_utils import save_eff, restore_eff, save_lambda_functions, bring_your_own_layer
from tao_byom.utils.convert_utils import test_diff, freeze_nodes, freeze_batchnorm, get_gpu_type


def build_command_line_parser(parser=None):
    """Parse command-line flags passed to the training script.

    Args:
        parser: Initial namespace.

    Returns:
        parser: Namespace with all parsed arguments.
    """
    if parser is None:
        parser = argparse.ArgumentParser(
            prog='BYOM Converter', description='Convert onnx model into TAO Model.')

    parser.add_argument(
        '-m',
        '--onnx_model_file',
        type=str,
        default=None,
        required=True,
        help='ONNX model path to the pre-trained weights.'
    )
    parser.add_argument(
        '-n',
        '--model_name',
        type=str,
        required=True,
        help='Name of the architecure inside onnx file'
    )
    parser.add_argument(
        '-r',
        '--results_dir',
        type=str,
        required=True,
        help='Path to a folder where converted Keras model will be stored.'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="log level NOTSET"
    )
    parser.add_argument(
        '-c',
        '--custom_meta',
        type=str,
        default=None,
        help='Path to custom meta json file that contains info about custom layer implementation'
    )
    parser.add_argument(
        '-k',
        '--key',
        type=str,
        default="nvidia-tao",
        help='Key to encrpyt tltb file'
    )
    parser.add_argument(
        '-p',
        '--penultimate_node',
        type=str,
        default=None,
        help='Name of ONNX node corresponding to the penultimate layer'
    )
    parser.add_argument(
        '-ki',
        '--kernel_initializer',
        type=str,
        default='glorot_uniform',
        choices=['glorot_uniform', 'glorot_normal',
                 'he_uniform', 'he_normal', 'zeros',
                 'random_uniform', 'random_normal',
                 'constant', 'ones', 'identity'],
        help='Type of kernel initializer used to initialize Conv, ConvTranspose, and Gemm'
    )
    parser.add_argument(
        "-fn",
        "--freeze_node", action='store',
        type=str, nargs='*',
        help="List of ONNX nodes to freeze. Examples: -i item1 item2",
        default=[])
    parser.add_argument(
        "-fb",
        '--freeze_bn',
        action='store_true',
        help="Whether to freeze every BatchNorm in the model."
    )
    return parser


def parse_command_line_args(cl_args=None):
    """Parser command line arguments to the trainer.

    Args:
        cl_args(sys.argv[1:]): Arg from the command line.

    Returns:
        args: Parsed arguments using argparse.
    """
    parser = build_command_line_parser(parser=None)
    args = parser.parse_args(cl_args)
    return args


def main(args=None):
    """Run the conversion process."""
    args = parse_command_line_args(args)

    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    input_path = args.onnx_model_file

    if not os.path.exists(input_path):
        raise FileNotFoundError("The provided onnx file does not exist!")

    os.makedirs(args.results_dir, exist_ok=True)

    logger = logging.getLogger(__name__)

    # For now channels_last is not supported
    change_ordering = False

    # Load ONNX model
    onnx_model = onnx.load(input_path)

    # Accessing Input Names
    input_all = [node.name for node in onnx_model.graph.input]
    input_initializer = [node.name for node in onnx_model.graph.initializer]
    net_feed_input = list(set(input_all) - set(input_initializer))

    opset = onnx_model.opset_import[0].version
    metadata = {"opset_version": opset,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "freeze_batchnorm": args.freeze_bn,
                "kernel_initializer": args.kernel_initializer,
                "model_name": args.model_name,
                "gpus": get_gpu_type(),
                "BYOM_version": tao_byom.__version__}

    # If custom implementation is provided, update our current converter.
    if args.custom_meta:
        additional_converters, custom_layer_file, custom_obj = bring_your_own_layer(meta_json_path=args.custom_meta)
        available_converters = {**AVAILABLE_CONVERTERS, **additional_converters}
    else:
        custom_layer_file, custom_obj = None, {}
        available_converters = AVAILABLE_CONVERTERS

    # Call the converter (net_feed_input - is the main model input name, can be different for your model)
    k_model, layer_mappings,  lambda_dicts = tao_byom_converter(onnx_model,
                                                                net_feed_input,
                                                                available_converters,
                                                                name_policy='renumerate',
                                                                kernel_initializer=args.kernel_initializer,
                                                                change_ordering=change_ordering,
                                                                opset=opset,
                                                                verbose=args.verbose
                                                                )

    # Only output layers upto the provided penultimate node
    if args.penultimate_node:
        if args.penultimate_node not in layer_mappings:
            raise ValueError(f"The provided penultimate node {args.penultimate_node} does not exist in the ONNX graph!")
        k_model = keras.Model(inputs=k_model.inputs, output=k_model.get_layer(layer_mappings[args.penultimate_node]).output)

    if args.verbose:
        logger.info("Converted Model Architecture before saving as an EFF")
        k_model.summary()

    # Test the difference between original ONNX and converted Keras Model
    test_diff(k_model, input_path, args.model_name, args.penultimate_node, epsilon=1e-4)

    # Save the model summary
    with open(os.path.join(args.results_dir, f'{args.model_name}_summary.txt'), mode='w', encoding="utf-8") as f:
        k_model.summary(print_fn=lambda x: f.write(x + '\n'))

    # Freeze layers. This part needs to be run after the diff check as output may vary
    # If freeze_node is present, freeze those layers
    if len(args.freeze_node):
        k_model, frozen_layers = freeze_nodes(k_model, args.freeze_node, layer_mappings)
        metadata['frozen_layers'] = frozen_layers

    # Freeze BatchNorms
    if args.freeze_bn:
        k_model = freeze_batchnorm(k_model)
        metadata['freeze_batchnorm'] = args.freeze_bn

    # Save names of lambda functions / custom layers used for conversion
    save_lambda_functions(lambda_dicts, args.results_dir, args.model_name)

    # Save model as EFF
    eff_path = save_eff(k_model,
                        args.results_dir,
                        args.model_name,
                        passphrase=args.key,
                        metadata=metadata,
                        custom_obj=custom_obj,
                        custom_layer_path=custom_layer_file,
                        verbose=args.verbose)
    eff_model, _ = restore_eff(args.model_name, eff_path, passphrase=args.key)

    if args.verbose:
        logger.info("Converted Model Architecture after saving as an EFF")
        eff_model.summary()

    logger.info("Saved model into EFF")


if __name__ == "__main__":
    main()
