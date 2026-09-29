# World Lobby four-trajectory comparison

Input: `/home/hchen/Documents/astraBlenderTest/vio-reconstruction/sessions/lobby_orb_success_20260929T123153/simulation_vio.mp4`

Primary ranking uses 4254 exact common native timestamps (source indices
245–4498). Each estimator receives one global SE(3) alignment with
scale fixed to 1. Sim(3) values are diagnostic only.

| Method | Coverage | Common | SE(3) ATE RMSE m | Median | P95 | Max | Rotation RMSE deg | Median | P95 | Max | Sim(3) scale | Sim(3) ATE RMSE m |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ORB-SLAM3 | 94.55% | 4254 | 0.1205 | 0.0839 | 0.2403 | 0.4030 | 0.1943 | 0.1572 | 0.3321 | 1.1719 | 0.977680 | 0.0259 |
| ViPE default | 100.00% | 4254 | 0.1668 | 0.1137 | 0.3355 | 0.3598 | 0.3065 | 0.2157 | 0.5410 | 0.8214 | 1.032927 | 0.0283 |
| OpenVINS | 98.73% | 4254 | 0.6721 | 0.4770 | 1.3714 | 1.5101 | 0.7699 | 0.1956 | 1.3061 | 4.6584 | 0.885078 | 0.0580 |

![Four trajectory comparison](trajectory_comparison.png)

All estimator outputs were frozen and hashed before ground truth was opened. Missing poses
were not interpolated or extrapolated.
