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
  viewers.push(viewer);
  controls.addEventListener("change", () => syncView(viewer));

  const resize = () => {
    const { width, height } = stage.getBoundingClientRect();
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };

  loader.load(
    stage.dataset.src,
    ({ scene: model }) => {
      scene.add(model);
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const radius = Math.max(size.x, size.y, size.z) * 0.62;
      viewer.center.copy(center);
      viewer.radius = radius;
      viewer.ready = true;
      controls.target.copy(center);
      camera.position.copy(center).add(new THREE.Vector3(radius, radius * 0.72, radius));
      camera.near = Math.max(radius / 1000, 0.01);
      camera.far = radius * 20;
      camera.updateProjectionMatrix();
      controls.update();
      const readySource = viewers.find((candidate) => candidate !== viewer && candidate.ready);
      if (readySource) syncView(readySource);
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
