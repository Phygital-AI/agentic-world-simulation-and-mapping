const C={zh:{t:["输入与建模路线","位姿、原生深度与模型深度","冻结模型几何","固定 5 视角外观","同场景 100 视角外观","固定 5 视角模型深度","同场景 100 视角模型深度"],view:"视角",l:{method:"方法",allowed_inputs:"允许输入",geometry_source:"几何来源",modeling_role:"建模角色",ate_m:"ATE (m) ↓",rotation_deg:"旋转误差 (°) ↓",native_depth_absrel:"原生深度 AbsRel ↓",model_depth_absrel:"模型深度 AbsRel ↓",alignment:"配准 / 限制",model_to_gt_mean_m:"模型→GT 均值 (m) ↓",observed_gt_to_model_mean_m:"观测 GT→模型均值 (m) ↓",bidirectional_mean_m:"双向平均 (m) ↓",model_sha256:"模型 SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"覆盖率 ↑",penalized_mae_m:"缺失惩罚 MAE (m) ↓"}},en:{t:["Inputs and modelling routes","Pose, native depth, and model depth","Frozen-model geometry","Fixed-five appearance","Same-scene 100-view appearance","Fixed-five model depth","Same-scene 100-view model depth"],view:"VIEW",l:{method:"Method",allowed_inputs:"Allowed inputs",geometry_source:"Geometry source",modeling_role:"Modelling role",ate_m:"ATE (m) ↓",rotation_deg:"Rotation (°) ↓",native_depth_absrel:"Native depth AbsRel ↓",model_depth_absrel:"Model depth AbsRel ↓",alignment:"Alignment / limitation",model_to_gt_mean_m:"Model→GT mean (m) ↓",observed_gt_to_model_mean_m:"Observed GT→model mean (m) ↓",bidirectional_mean_m:"Bidirectional mean (m) ↓",model_sha256:"Model SHA256",psnr_db:"PSNR (dB) ↑",ssim:"SSIM ↑",lpips_alex_v01:"LPIPS ↓",absrel:"AbsRel ↓",rmse_m:"RMSE (m) ↓",coverage:"Coverage ↑",penalized_mae_m:"Penalized MAE (m) ↓"}}};
const lang = document.body.dataset.lang === "zh" ? "zh" : "en";
const c = C[lang];
const methodNames = {
  en: {M1: "RGB-only", M2: "ViPE + DA3", M3: "ORB-SLAM3 + DA3", M4: "GT pose + DA3"},
  zh: {M1: "纯 RGB", M2: "ViPE + DA3", M3: "ORB-SLAM3 + DA3", M4: "GT 位姿 + DA3"}
};
const methodLabel = id => methodNames[lang][id] ? `${id} (${methodNames[lang][id]})` : id;
// Display translations are separate from the frozen experimental data.
const routeText = {
  en: {
    M1: {allowed_inputs: "180 sampled RGB frames", geometry_source: "Visual inference without measured scale", modeling_role: "Infer the layout and author objects and materials"},
    M2: {allowed_inputs: "Full RGB video; 180 frames selected for modeling", geometry_source: "RGB-only ViPE poses → pose-conditioned DA3 depth", modeling_role: "Organize pose and depth measurements into an object-centric scene"},
    M3: {allowed_inputs: "Video, IMU, and camera–IMU calibration", geometry_source: "Monocular-inertial ORB-SLAM3 poses → pose-conditioned DA3 depth", modeling_role: "Model using images, poses, and depth"},
    M4: {allowed_inputs: "Video and ground-truth camera poses", geometry_source: "GT poses → pose-conditioned DA3 depth", modeling_role: "The same type of modeling workflow as M3"}
  },
  zh: {
    M1: {allowed_inputs: "180 张采样 RGB 图像", geometry_source: "视觉推断，无测量尺度", modeling_role: "推断布局，编写对象与材质"},
    M2: {allowed_inputs: "完整 RGB 视频；选取 180 帧建模", geometry_source: "仅基于 RGB 的 ViPE 位姿 → 位姿条件下的 DA3 深度", modeling_role: "将位姿与深度测量组织为对象化场景"},
    M3: {allowed_inputs: "视频、IMU、相机–IMU 标定", geometry_source: "ORB-SLAM3 单目惯性位姿 → 位姿条件下的 DA3 深度", modeling_role: "结合图像、位姿、深度建模"},
    M4: {allowed_inputs: "视频及真值相机位姿", geometry_source: "真值位姿 → 位姿条件下的 DA3 深度", modeling_role: "与 M3 相同类型的建模流程"}
  }
};
const directions = {
  ate_m: "min", rotation_deg: "min", native_depth_absrel: "min", model_depth_absrel: "min",
  model_to_gt_mean_m: "min", observed_gt_to_model_mean_m: "min", bidirectional_mean_m: "min",
  psnr_db: "max", ssim: "max", lpips_alex_v01: "min", absrel: "min", rmse_m: "min",
  coverage: "max", penalized_mae_m: "min"
};
const hidden = {2: new Set(["alignment"]), 3: new Set(["model_sha256", "alignment"])};
function formatCell(key, value) {
  if (value === null) return "—";
  if (key === "method") return methodLabel(value);
  if (typeof value !== "number") return String(value).replace(/\bM[1-4]\b/g, methodLabel);
  return ["native_depth_absrel", "model_depth_absrel", "absrel", "coverage"].includes(key)
    ? (100 * value).toFixed(2) + "%" : value.toFixed(4);
}
fetch("data/tables_1_7.json").then(response => {
  if (!response.ok) throw Error(response.status);
  return response.json();
}).then(data => {
  for (let number = 1; number <= 7; number++) {
    const figure = document.querySelector("#table-" + number);
    if (!figure) continue;
    const rows = data.tables["table" + number];
    const keys = Object.keys(rows[0]).filter(key => !hidden[number]?.has(key));
    const best = {};
    for (const key of keys) {
      if (!directions[key]) continue;
      const values = rows.map(row => row[key]).filter(value => typeof value === "number" && Number.isFinite(value));
      if (values.length) best[key] = (directions[key] === "max" ? Math.max : Math.min)(...values);
    }
    figure.querySelector(".table-title").textContent = c.t[number - 1];
    const table = document.createElement("table");
    const header = table.createTHead().insertRow();
    for (const key of keys) {
      const cell = document.createElement("th");
      cell.scope = "col";
      cell.textContent = c.l[key] || key;
      header.append(cell);
    }
    const body = table.createTBody();
    for (const row of rows) {
      const tr = body.insertRow();
      keys.forEach((key, index) => {
        const cell = document.createElement(index ? "td" : "th");
        if (!index) cell.scope = "row";
        if (["allowed_inputs", "geometry_source", "modeling_role", "alignment"].includes(key)) cell.className = "wrap";
        const value = number === 1 ? routeText[lang][row.method]?.[key] ?? row[key] : row[key];
        const text = formatCell(key, value);
        if (typeof row[key] === "number" && row[key] === best[key]) {
          const strong = document.createElement("strong");
          strong.textContent = text;
          cell.append(strong);
        } else cell.textContent = text;
        tr.append(cell);
      });
    }
    figure.querySelector(".table-mount").replaceChildren(table);
  }
}).catch(error => {
  document.querySelectorAll(".table-mount").forEach(mount => {
    mount.textContent = (lang === "zh" ? "表格加载失败：" : "Table load failed: ") + error.message;
  });
  console.error(error);
});
const method = document.querySelector("#compare-method");
const frame = document.querySelector("#compare-frame");
method.disabled = false;
frame.disabled = false;
function refresh() {
  const id = String(frame.value).padStart(3, "0"), m = method.value;
  document.querySelector("#compare-pred").src = `assets/fixed_views/${m}/${id}.png`;
  document.querySelector("#compare-gt").src = `assets/fixed_views/GT/${id}.png`;
  document.querySelector("#compare-label").textContent = `${m} / ${c.view} ${frame.value}`;
  document.querySelector("#figure-5").dataset.method = m;
  document.querySelector("#figure-5").dataset.frame = frame.value;
}
method?.addEventListener("change", refresh);
frame?.addEventListener("change", refresh);
refresh();
