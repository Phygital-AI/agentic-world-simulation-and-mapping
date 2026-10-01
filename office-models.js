import * as THREE from "three";
import { GLTFLoader } from "./vendor/three/loaders/GLTFLoader.js";
import { OrbitControls } from "./vendor/three/controls/OrbitControls.js";

const stylesheet = document.createElement("link");
stylesheet.rel = "stylesheet";
stylesheet.href = "./office.css";
document.head.append(stylesheet);

const stages = [...document.querySelectorAll(".office-model-stage")];
const loader = new GLTFLoader();
const viewers = [];
let syncingView = false;

function syncView(source) {
  if (syncingView || !source.ready) return;
  syncingView = true;
  const sourceTargetOffset = source.controls.target.clone().sub(source.center);
  const sourceCameraOffset = source.camera.position.clone().sub(source.controls.target);
  for (const viewer of viewers) {
    if (viewer === source || !viewer.ready) continue;
    const scale = viewer.radius / source.radius;
    viewer.controls.target.copy(viewer.center).addScaledVector(sourceTargetOffset, scale);
    viewer.camera.position.copy(viewer.controls.target).addScaledVector(sourceCameraOffset, scale);
    viewer.controls.update();
  }
  syncingView = false;
}

function mount(stage) {
  if (stage.dataset.loaded) return;
  stage.dataset.loaded = "true";

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xe9ede5);

  const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 500);
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  stage.replaceChildren(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x8b948c, 2.2));
  const sun = new THREE.DirectionalLight(0xfff4dc, 2.8);
  sun.position.set(8, 14, 10);
  scene.add(sun);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.screenSpacePanning = true;
  const viewer = {
    stage,
    camera,
    controls,
    center: new THREE.Vector3(),
    radius: 1,
    ready: false,
  };
  const zh = document.documentElement.lang.startsWith("zh");
  const toolbar = document.createElement("div");
  toolbar.style.cssText = "position:absolute;top:10px;left:10px;display:flex;gap:8px;z-index:1";
  const reset = document.createElement("button");
  reset.type = "button";
  reset.textContent = zh ? "重置视角" : "Reset view";
  const cutaway = document.createElement("button");
  cutaway.type = "button";
  cutaway.textContent = zh ? "剖切视图" : "Cutaway";
  cutaway.setAttribute("aria-pressed", "true");
  for (const button of [reset, cutaway]) {
    button.style.cssText = "padding:6px 10px;border:1px solid #bdcbbf;border-radius:4px;background:#fffffff0;color:#196451;font:12px sans-serif;cursor:pointer";
    toolbar.append(button);
  }
  stage.append(toolbar);
  let sectionPlane;
  let initialDistance = 1;
  let previousAspect = 1;
  const direction = new THREE.Vector3(0.45, 1, 0.65).normalize();
  const resetView = () => {
    if (!viewer.ready) return;
    const damping = controls.enableDamping;
    controls.enableDamping = false;
    controls.update();
    controls.target.copy(viewer.center);
    camera.position.copy(viewer.center).addScaledVector(direction, initialDistance);
    controls.update();
    controls.enableDamping = damping;
    syncView(viewer);
  };
  reset.addEventListener("click", resetView);
  cutaway.addEventListener("click", () => {
    const enabled = cutaway.getAttribute("aria-pressed") !== "true";
    cutaway.setAttribute("aria-pressed", String(enabled));
    renderer.clippingPlanes = enabled && sectionPlane ? [sectionPlane] : [];
  });
  viewers.push(viewer);
  controls.addEventListener("change", () => syncView(viewer));

  const resize = () => {
    const { width, height } = stage.getBoundingClientRect();
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    if (viewer.ready) {
      const factor = Math.max(1, 1 / camera.aspect) / Math.max(1, 1 / previousAspect);
      initialDistance *= factor;
      camera.position.sub(controls.target).multiplyScalar(factor).add(controls.target);
    }
    previousAspect = camera.aspect;
    camera.updateProjectionMatrix();
  };

  loader.load(
    stage.dataset.src,
    ({ scene: model }) => {
      scene.add(model);
      const fullBox = new THREE.Box3().setFromObject(model);
      const sectionHeight = fullBox.min.y + (fullBox.max.y - fullBox.min.y) * 0.64;
      const box = new THREE.Box3();
      model.traverse((node) => {
        if (!node.isMesh) return;
        const meshBox = new THREE.Box3().setFromObject(node);
        if (meshBox.min.y > sectionHeight) return;
        meshBox.max.y = Math.min(meshBox.max.y, sectionHeight);
        box.union(meshBox);
      });
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const radius = box.getBoundingSphere(new THREE.Sphere()).radius;
      center.y = box.min.y + size.y * 0.25;
      viewer.center.copy(center);
      viewer.radius = radius;
      sectionPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), sectionHeight);
      renderer.clippingPlanes = cutaway.getAttribute("aria-pressed") === "true" ? [sectionPlane] : [];
      initialDistance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * Math.max(1, 1 / camera.aspect);
      viewer.ready = true;
      camera.near = Math.max(radius / 1000, 0.01);
      camera.far = radius * 20;
      camera.updateProjectionMatrix();
      const readySource = viewers.find((candidate) => candidate !== viewer && candidate.ready);
      if (readySource) syncView(readySource);
      else resetView();
      stage.dataset.ready = "true";
      stage.sceneDiagnostics = () => ({
        ready: viewer.ready,
        camera: camera.position.toArray(),
        target: controls.target.toArray(),
        cutaway: renderer.clippingPlanes.length > 0,
        sectionHeight: sectionPlane.constant,
        bounds: { min: box.min.toArray(), max: box.max.toArray() },
      });
    },
    undefined,
    () => {
      stage.classList.add("is-error");
      stage.insertAdjacentHTML("beforeend", "<p>Model failed to load.</p>");
    },
  );

  new ResizeObserver(resize).observe(stage);
  resize();

  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}

if (stages.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          mount(entry.target);
          observer.unobserve(entry.target);
        }
      }
    },
    { rootMargin: "300px" },
  );
  stages.forEach((stage) => observer.observe(stage));
}

const syncedVideos = [...document.querySelectorAll("[data-synced-video]")];
const videoPlay = document.querySelector(".office-video-play");
const videoProgress = document.querySelector(".office-video-progress");
const videoTime = document.querySelector(".office-video-time");

if (syncedVideos.length === 2 && videoPlay && videoProgress && videoTime) {
  const primary = syncedVideos[0];
  const formatTime = (seconds) => {
    const safe = Number.isFinite(seconds) ? seconds : 0;
    return `${String(Math.floor(safe / 60)).padStart(2, "0")}:${String(Math.floor(safe % 60)).padStart(2, "0")}`;
  };
  const updateProgress = () => {
    if (!primary.duration || videoProgress.matches(":active")) return;
    videoProgress.value = String((primary.currentTime / primary.duration) * 1000);
    videoTime.textContent = `${formatTime(primary.currentTime)} / ${formatTime(primary.duration)}`;
  };
  const setPlaying = (playing) => {
    videoPlay.textContent = playing ? "❚❚" : "▶";
    videoPlay.setAttribute("aria-label", playing ? "Pause both videos" : "Play both videos");
  };

  syncedVideos.forEach((video) => {
    video.muted = true;
    video.playsInline = true;
  });
  primary.addEventListener("loadedmetadata", updateProgress);
  primary.addEventListener("timeupdate", updateProgress);
  primary.addEventListener("ended", () => {
    syncedVideos.forEach((video) => video.pause());
    setPlaying(false);
  });
  videoProgress.addEventListener("input", () => {
    const fraction = Number(videoProgress.value) / 1000;
    syncedVideos.forEach((video) => {
      if (video.duration) video.currentTime = fraction * video.duration;
    });
    updateProgress();
  });
  videoPlay.addEventListener("click", async () => {
    if (primary.paused) {
      await Promise.all(syncedVideos.map((video) => video.play()));
      setPlaying(true);
    } else {
      syncedVideos.forEach((video) => video.pause());
      setPlaying(false);
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      syncedVideos.forEach((video) => video.pause());
      setPlaying(false);
    }
  });
  updateProgress();
}
