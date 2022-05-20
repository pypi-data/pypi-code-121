# filename and full path for saving the prediction files (without segmentation)
PRED_PATH = "{path}{output_name}{dtype_sep}{tag}{sep_timetag}.csv"
PRED_PATH_CHUNK = "{path}{output_name}{dtype_sep}{tag}{sep_timetag}_{index}.csv"
PRED_FILENAME = "{output_name}{dtype_sep}{tag}{sep_timetag}.csv"

# filename and full path for saving the prediction files (with segmentation)
PRED_PATH_SEG = "{path}{output_name}{dtype_sep}{tag}{sep_timetag}_{seg_id}.csv"
PRED_PATH_CHUNK_SEG = "{path}{output_name}{dtype_sep}{tag}{sep_timetag}_{seg_id}{sep_index}.csv"
PRED_FILENAME_SEG = "{output_name}{dtype_sep}{tag}{sep_timetag}_{index}.csv"
PRED_FILENAME_CHUNK_SEG = "{output_name}{dtype_sep}{tag}{sep_timetag}_{seg_id}{sep_index}.csv"


SAVE_MODEL_PATH = "{path}{output_name}_{tag}{sep_timetag}{ext}"
SAVE_MODEL_PATH_SEG = "{path}{output_name}_{tag}_{seg_id}{sep_timetag}{ext}"
SAVE_MODEL_PATH_EPOCH = "{path}{output_name}_{tag}_{epoch}{sep_timetag}{ext}"
LOAD_MODEL_PATH_SEG = "{path}{prefix}_{seg_id}{sep_timetag}{ext}"

FEATURE_IMPORTANCE_PATH = "{output_name}_{tag}_feature_importance{sep_timetag}"
FEATURE_IMPORTANCE_PATH_SEG = "{output_name}_{tag}_{seg_id}_feature_importance{sep_timetag}"

PREDICTIONS_VS_ACTUALS_PLOT = "{path}{output_name}_{tag}_predictions_vs_actuals{sep_timetag}.png"

SHAP_PATH = "{output_name}_{tag}_shap_values{class_name}{sep_timetag}.csv"
SHAP_PLOT = "{path}{output_name}_{tag}_shap_{type}{sep_timetag}.png"
SHAP_PLOT_ClASS = "{path}{output_name}_{tag}_shap_{type}_{class_name}{sep_timetag}.png"

TRAIN_VALIDATION_SPLIT = "{output_name}_{dtype}_split{sep_timetag}.{format}"

LEARNING_RATE = "{path}{output_name}_{tag}_learning_rate{sep_timetag}.png"
