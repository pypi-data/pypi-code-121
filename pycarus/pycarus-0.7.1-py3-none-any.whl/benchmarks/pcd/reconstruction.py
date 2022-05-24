from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

import torch

from pycarus.geometry.pcd import read_pcd
from pycarus.metrics.chamfer_distance import chamfer
from pycarus.metrics.emd_distance import emd
from pycarus.metrics.f_score import f_score
from pycarus.utils import progress_bar

T_RESULTS_DICT = Dict[str, List[float]]


def _get_gts_and_preds_paths(gt_dir: Path, pred_dir: Path) -> Tuple[List[Path], List[Path]]:
    """Get ground-truths and predictions file path.

    Args:
        gt_dir: The path to the directory with all the ground-truths.
        pred_dir: The path to the directory with all the predictions.

    Returns:
        - A list with all ground-truth paths.
        - A list with all predictions paths.
    """
    gt_files = []
    pred_files = []
    categories_dirs = [subdir for subdir in gt_dir.iterdir() if subdir.is_dir()]
    for category_dir in categories_dirs:
        for gt_file in category_dir.glob("*.ply"):
            gt_files.append(gt_file)
            pred_files.append(pred_dir / category_dir.name / gt_file.name)

    return gt_files, pred_files


def _compute_single_results(
    gt_dir: Path,
    pred_dir: Path,
    results_dir: Path,
    batch_size: int,
    gpu: bool,
    compute_emd: bool,
) -> Tuple[T_RESULTS_DICT, T_RESULTS_DICT, T_RESULTS_DICT, T_RESULTS_DICT]:
    """Compute results for every single item and save them in the
    proper results file.

    Args:
        gt_dir: The path to the directory with all the ground-truths.
        pred_dir: The path to the directory with all the predictions.
        results_dir: The path to the output directory.
        batch_size: The batch size to use for computations.
        gpu: Whether to use or not gpu for computations.
        compute_emd: Whether to compute or not emd.

    Returns:
        - A dict with cd_p results for all categories.
        - A dict with cd_t results for all categories.
        - A dict with f1_score results for all categories.
        - A dict with emd results for all categories.
    """
    single_results_file = results_dir / "single_results.csv"
    if single_results_file.exists():
        single_results_file.unlink()

    with open(single_results_file, "wt") as f:
        f.write("CATEGORY/NAME,CD_P,CD_T,F1-SCORE")
        f.write(",EMD\n" if compute_emd else "\n")

    cd_ps = defaultdict(list)
    cd_ts = defaultdict(list)
    f1_scores = defaultdict(list)
    emds = defaultdict(list)

    gt_files, pred_files = _get_gts_and_preds_paths(gt_dir, pred_dir)

    num_batches = len(gt_files) // batch_size
    num_batches = num_batches + 1 if len(gt_files) % batch_size != 0 else num_batches

    for batch in progress_bar(range(num_batches)):
        start = batch * batch_size
        end = start + batch_size
        gt_files_batch = gt_files[start:end]
        pred_files_batch = pred_files[start:end]

        gts = torch.stack([read_pcd(gt_file) for gt_file in gt_files_batch], dim=0)
        preds = torch.stack([read_pcd(pred_file) for pred_file in pred_files_batch], dim=0)

        if gpu:
            gts = gts.cuda()
            preds = preds.cuda()

        _, cds_pred_gt, cds_gt_pred, _, _ = chamfer(preds, gts, squared=False)
        _, cds_pred_gt_sq, cds_gt_pred_sq, _, _ = chamfer(preds, gts, squared=True)
        f1s, _, _ = f_score(preds.cpu(), gts.cpu(), threshold=0.01)
        if compute_emd:
            emds_, _ = emd(preds, gts, eps=0.004, iterations=3000, squared=False, reduction="mean")

        for i, gt_file in enumerate(gt_files_batch):
            category = gt_file.parent.name
            shape_name = gt_file.stem

            cd_p = float(((cds_gt_pred[i] + cds_pred_gt[i]) / 2).item())
            cd_ps["all"].append(cd_p)
            cd_ps[category].append(cd_p)

            cd_t = float((cds_gt_pred_sq[i] + cds_pred_gt_sq[i]).item())
            cd_ts["all"].append(cd_t)
            cd_ts[category].append(cd_t)

            if compute_emd:
                emd_ = float(emds_[i].item())
                emds["all"].append(emd_)
                emds[category].append(emd_)

            f1_score = float(f1s[i].item())
            f1_scores["all"].append(f1_score)
            f1_scores[category].append(f1_score)

            with open(single_results_file, "at") as f:
                line = f"{category}/{shape_name},{cd_p:.8f},{cd_t:.8f},{f1_score:.8f}"
                line += f",{emd_:.8f}\n" if compute_emd else "\n"
                f.write(line)

    return cd_ps, cd_ts, f1_scores, emds


def _compute_global_results(
    results_dir: Path,
    cd_ps: T_RESULTS_DICT,
    cd_ts: T_RESULTS_DICT,
    f1_scores: T_RESULTS_DICT,
    emds: T_RESULTS_DICT,
    compute_emd: bool,
) -> None:
    """Compute global results and save them in the proper results file.

    Args:
        results_dir: The path to the output directory.
        cd_ps: The dict with cd_p results for all categories.
        cd_ts: The dict with cd_t results for all categories.
        f1_scores: The dict with f1_score results for all categories.
        emds: The dict with emd results for all categories.
        compute_emd: Whether to compute or not emd.
    """
    global_results_file = results_dir / "global_results.csv"
    if global_results_file.exists():
        global_results_file.unlink()

    with open(global_results_file, "wt") as f:
        f.write("CATEGORY,CD_P,CD_T,F1-SCORE")
        f.write(",EMD\n" if compute_emd else "\n")

    for category in sorted(cd_ps.keys()):
        if category != "all":
            m_cd_p = mean(cd_ps[category])
            m_cd_t = mean(cd_ts[category])
            m_f1_score = mean(f1_scores[category])
            if compute_emd:
                m_emd_ = mean(emds[category])

            with open(global_results_file, "at") as f:
                f.write(f"{category},{m_cd_p:.8f},{m_cd_t:.8f},{m_f1_score:.8f}")
                f.write(f",{m_emd_:.8f}\n" if compute_emd else "\n")

    with open(global_results_file, "at") as f:
        f.write("\n\n")
        f.write(f"MEAN CD_P,{mean(cd_ps['all']):.8f}\n")
        f.write(f"MEAN CD_T,{mean(cd_ts['all']):.8f}\n")
        f.write(f"MEAN F1 SCORE,{mean(f1_scores['all']):.8f}\n")
        if compute_emd:
            f.write(f"MEAN EMD,{mean(emds['all']):.8f}\n")


def pcd_reconstruction_evaluation(
    gt_dir: Path,
    pred_dir: Path,
    results_dir: Path,
    batch_size: int = 512,
    gpu: bool = True,
    compute_emd: bool = True,
) -> None:
    """Evaluate point cloud reconstruction results.

    The function requires the ground-truth clouds and the predicted ones to be
    organized in two separate directories with the same structure. Each directory
    must contain one sub-directory for each category and each subdirectory must
    contain one .ply file for each cloud. The function expects the name of the files
    in the "gt_dir" and "pred_dir" directories to be matching in order to perform
    the comparison.

    Four metrics are computed: the two Chamfer Distances proposed in the paper
    "Variational Relational Point Completion Network.", Earth Mover's Distance and F1 score.
    Results are saved into two files ("global_results.csv" and "single_results.csv")
    inside the given "result_dir" directory.

    Args:
        gt_dir: Directory with ground-truth clouds.
        pred_dir: Directory with predicted clouds.
        results_dir: Directory where the .csv files with the results will be saved.
        batch_size: The batch size to use for computing metrics. Defaults to 512.
        gpu: Whether to use gpu or not to compute metrics. Defaults to True.
        compute_emd: Whether to compute or not EMD. Defaults to True.

    Raises:
        ValueError: If one prediction is missing.
    """
    results_dir.mkdir(parents=True, exist_ok=True)

    cd_ps, cd_ts, f1_scores, emds = _compute_single_results(
        gt_dir,
        pred_dir,
        results_dir,
        batch_size,
        gpu,
        compute_emd,
    )

    _compute_global_results(results_dir, cd_ps, cd_ts, f1_scores, emds, compute_emd)
