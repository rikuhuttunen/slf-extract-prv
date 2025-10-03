import argparse
import logging
import numpy as np
import sleeplab_format as slf

from pathlib import Path
from scipy.interpolate import interp1d
from systole.correction import correct_peaks
from systole.detection import ppg_peaks
from tqdm import tqdm


logger = logging.getLogger(__name__)


def extract_and_save(
        ds_dir: Path,
        ppg_key: str = 'Pleth_64Hz',
        fs_interp: float = 5.0,
        peak_detection_method: str = 'msptd',
        peak_detection_window_length: int = 60,
        peak_detection_overlap: float = 0.2,
        savedir: Path | None = None) -> None:
    """Extract PPG peaks and interpolate the inter-beat interval time series with given sampling frequency.
    
    Args:
        savedir: if given, save the peaks and interpolated IBI signal there. Otherwise, save within the dataset.
    """
    logger.info(f'Reading dataset from {ds_dir}...')
    ds = slf.reader.read_dataset(ds_dir, include_annotations=False)

    for series in ds.series.values():
        logger.info(f'Extracting PPG peaks and interpolating IBIs for series {series.name}...')
        for subj in tqdm(series.subjects.values()):
            try:
                ppg = subj.sample_arrays[ppg_key]
            except KeyError:
                logger.info(f'Subject {subj.metadata.subject_id}: sample array with key {ppg_key} not found, skipping...')

            ppg_fs = ppg.attributes.sampling_rate
            try:
                _, peaks_idx = ppg_peaks(
                    ppg.values,
                    ppg_fs,
                    verbose=True,
                    method=peak_detection_method,
                    detector_kws={'win_len': peak_detection_window_length, 'overlap': peak_detection_overlap}
                )
            except ValueError as e:
                logger.info(f'Subject {subj.metadata.subject_id}: skipping due to ValueError: {repr(e)}')
                continue

            corrected_idx = correct_peaks(peaks_idx, n_iterations=2, verbose=False)
            # ppg_peaks returns peaks in 1000 Hz array of booleans, where peaks are indicated with True.
            # Transform these 
            clean_peaks_idx = np.where(corrected_idx['clean_peaks'])[0]

            # Create an SLF sample array from clean peaks. As a hack, set sampling interval to -1 to indicate uneven sampling
            peak_attributes = slf.models.ArrayAttributes(
                name=f'{ppg_key}_peaks',
                start_ts=ppg.attributes.start_ts,
                sampling_interval=-1.0,
                unit='ms'
            )

            # Calculate the IBIs and interpolate to the desired sampling frequency
            # TODO: How should we handle physically impossible IBIs
            ibi_ms = np.diff(clean_peaks_idx)
            t_ms = np.cumsum(ibi_ms) + clean_peaks_idx[0] - ibi_ms[0]
            f = interp1d(t_ms, ibi_ms, kind='cubic', fill_value='extrapolate')
            ppg_len_s = len(ppg.values) / ppg_fs
            t_interp = np.linspace(0, 1000 * ppg_len_s, int(fs_interp * ppg_len_s))
            ibi_interp = f(t_interp)
            ibi_attributes = slf.models.ArrayAttributes(
                name=f'{ppg_key}_ibi_{int(fs_interp)}_Hz',
                start_ts=ppg.attributes.start_ts,
                sampling_rate=fs_interp,
                unit='ms'
            )

            if savedir is None:
                subject_path = ds_dir / series.name / subj.metadata.subject_id
            else:
                subject_path = savedir / ds_dir.name / series.name / subj.metadata.subject_id

            # Write the peak indices in milliseconds
            peaks_path = subject_path / peak_attributes.name
            peaks_path.mkdir(exist_ok=True, parents=True)
            peaks_attr_path = peaks_path / 'attributes.json'
            peaks_attr_path.write_text(
                peak_attributes.model_dump_json(indent=2, exclude_none=True)
            )
            np.save(peaks_path / 'data.npy', clean_peaks_idx, allow_pickle=False)

            # Write the IBI time series similarly to peaks
            ibi_path = subject_path / ibi_attributes.name
            ibi_path.mkdir(exist_ok=True, parents=True)
            ibi_attr_path = ibi_path / 'attributes.json'
            ibi_attr_path.write_text(
                ibi_attributes.model_dump_json(indent=2, exclude_none=True)
            )
            np.save(ibi_path / 'data.npy', ibi_interp.astype(np.float32), allow_pickle=False)

    return None


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ds-dir', type=Path, required=True,
        help='The sleeplab-format dataset directory path')
    parser.add_argument('--ppg-key', default='Pleth',
        help='The name of the PPG signal in the dataset')
    parser.add_argument('--fs-interp', type=float, default=5.0,
        help='The sampling frequency of the interpolated inter-beat-interval timeseries')
    parser.add_argument('--savedir', type=Path, default=None,
        help='Optional save root directory. By default, the results are saved within the SLF dataset')
    parser.add_argument('--peak-detection-method', type=str, default='msptd',
        help='The method argument for systole.detection.ppg_peaks')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    extract_and_save(**vars(args))
