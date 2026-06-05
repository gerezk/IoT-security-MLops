from datetime import timezone, datetime

import mlflow
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


def run_msg_freq_drift_detection(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
    alpha: float = 0.05,
) -> dict:
    """
    Detects per-sensor drift in messaging frequency using the Kolmogorov-Smirnov test. \n
    Assumed that the set for ip.src is the same for the reference and current dfs.
    :param reference_df: Baseline dataset used during training.
    :param current_df: Newly observed production/post-deployment dataset.
    :param alpha: Significance threshold for KS test.
    :return: dict of test results that will be dumped to json.
    """
    src_ip_set = reference_df["ip.src"].unique()

    reference_df_copy = reference_df.copy()
    current_df_copy = current_df.copy()

    # drop all cols except ip.src and msg_freq
    reference_df_copy = reference_df_copy[["ip.src", "msg_freq"]]
    current_df_copy = current_df_copy[["ip.src", "msg_freq"]]

    drift_results = {}

    total_ips_drifted = 0

    for ip in src_ip_set:
        if len(reference_df_copy) == 0 or len(current_df_copy) == 0:
            continue

        ref_ip_msg_freq = reference_df_copy[reference_df_copy["ip.src"] == ip]
        current_ip_msg_freq = current_df_copy[current_df_copy["ip.src"] == ip]

        # keep only msg_freq col
        ref_ip_msg_freq = ref_ip_msg_freq["msg_freq"]
        current_ip_msg_freq = current_ip_msg_freq["msg_freq"]

        statistic, p_value = ks_2samp(ref_ip_msg_freq, current_ip_msg_freq)

        drift_detected = bool(p_value < alpha)

        if drift_detected:
            total_ips_drifted += 1

        drift_results[ip] = {
            "ks_statistic": float(statistic),
            "p_value": float(p_value),
            "drift_detected": drift_detected,
            "reference_mean": float(np.mean(ref_ip_msg_freq)),
            "current_mean": float(np.mean(current_ip_msg_freq)),
            "reference_std": float(np.std(ref_ip_msg_freq)),
            "current_std": float(np.std(current_ip_msg_freq)),
        }

    overall_status = (
        "drift_detected"
        if total_ips_drifted > 0
        else "stable"
    )

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "monitoring_status": overall_status,
        "alpha": alpha,
        "total_ips": len(src_ip_set),
        "drifted_ips": total_ips_drifted,
        "ips": drift_results,
    }

    return report