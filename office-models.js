import * as THREE from "three";
import { GLTFLoader } from "./vendor/three/loaders/GLTFLoader.js";
import { OrbitControls } from "./vendor/three/controls/OrbitControls.js";

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
const videoStatus = document.querySelector(".office-video-status");

if (syncedVideos.length === 3 && videoPlay && videoProgress && videoTime && videoStatus) {
  const primary = syncedVideos[0];
  const zh = document.documentElement.lang.startsWith("zh");
  const copy = zh ? {
    play: "播放全部三个视频", pause: "暂停全部三个视频",
    ready: "同步播放 · 70.1 秒 · 30 fps", waiting: "正在加载，三个视频就绪后将同步播放…",
    interrupted: "播放已中断，请点击播放继续。",
    failedVideo: (name) => `${name}加载失败，请点击播放重试。`,
  } : {
    play: "Play all three videos", pause: "Pause all three videos",
    ready: "Shared playback · 70.1 seconds · 30 fps", waiting: "Loading — all three videos will start together…",
    interrupted: "Playback was interrupted. Press play to continue.",
    failedVideo: (name) => `Unable to load ${name}. Press play to retry.`,
  };
  let wanted = false;
  let waiting = false;
  let starting = false;
  let generation = 0;
  let targetTime = 0;
  let startRetries = 0;
  let retryAt = 0;
  const duration = () => Number.isFinite(primary.duration) ? primary.duration : 70.1;
  const formatTime = (seconds) => {
    const safe = Number.isFinite(seconds) ? seconds : 0;
    return `${String(Math.floor(safe / 60)).padStart(2, "0")}:${String(Math.floor(safe % 60)).padStart(2, "0")}`;
  };
  const updateProgress = () => {
    const time = waiting ? targetTime : primary.currentTime;
    if (!videoProgress.matches(":active")) videoProgress.value = String((time / duration()) * 1000);
    videoTime.textContent = `${formatTime(time)} / ${formatTime(duration())}`;
    videoProgress.setAttribute("aria-valuetext", videoTime.textContent);
  };
  const setPlaying = (playing) => {
    videoPlay.textContent = playing ? "❚❚" : "▶";
    videoPlay.setAttribute("aria-label", playing ? copy.pause : copy.play);
    videoPlay.setAttribute("aria-pressed", String(playing));
  };
  const pauseAll = () => syncedVideos.forEach((video) => {
    video.pause();
    video.playbackRate = 1;
  });
  const align = () => syncedVideos.forEach((video) => {
    if (Number.isFinite(video.duration) && Math.abs(video.currentTime - targetTime) > 0.04) {
      video.currentTime = Math.min(targetTime, video.duration);
    }
  });
  const stop = (message = copy.ready) => {
    wanted = waiting = starting = false;
    generation += 1;
    pauseAll();
    setPlaying(false);
    videoStatus.textContent = message;
    updateProgress();
  };
  const ready = () => syncedVideos.every((video) => !video.seeking && video.readyState >= 3);
  const bufferedAhead = (video) => {
    for (let i = 0; i < video.buffered.length; i += 1) {
      if (video.buffered.start(i) <= video.currentTime + 0.05 && video.buffered.end(i) > video.currentTime) {
        return video.buffered.end(i) - video.currentTime;
      }
    }
    return 0;
  };
  // Some browsers stop preloading after a small byte budget. Let an idle
  // decoder start so play() can resume the download; active downloads can
  // build a buffer first. This also avoids a play/pause loop on slow links.
  const buffered = () => syncedVideos.every((video) => {
    // A paused decoder may stay at HAVE_CURRENT_DATA until play() is called,
    // even with future bytes buffered. Requiring canplay here can deadlock.
    if (video.seeking || video.error || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return false;
    if (video.networkState === HTMLMediaElement.NETWORK_IDLE) return true;
    return bufferedAhead(video) >= Math.min(0.5, Math.max(0, video.duration - video.currentTime - 0.05));
  });
  const resume = async () => {
    if (!wanted || !waiting || starting || performance.now() < retryAt || !buffered()) return;
    const attempt = ++generation;
    waiting = false;
    starting = true;
    const results = await Promise.allSettled(syncedVideos.map((video) => video.play()));
    if (attempt !== generation) return;
    starting = false;
    const rejected = results.find((result) => result.status === "rejected");
    if (rejected) {
      // pause(), seeking and load() can cancel play() without a media failure.
      const mediaFailure = syncedVideos.find((video) => video.error);
      if (!mediaFailure && rejected.reason?.name === "AbortError" && startRetries < 2) {
        startRetries += 1;
        targetTime = Math.min(...syncedVideos.map((video) => video.currentTime));
        pauseAll();
        align();
        waiting = true;
        retryAt = performance.now() + 250;
        videoStatus.textContent = copy.waiting;
        return;
      }
      stop(mediaFailure ? copy.failedVideo(mediaFailure.getAttribute("aria-label")) : copy.interrupted);
      return;
    }
    startRetries = 0;
    videoStatus.textContent = copy.ready;
  };
  const hold = (time = primary.currentTime) => {
    generation += 1;
    starting = false;
    waiting = true;
    targetTime = time;
    pauseAll();
    align();
    if (wanted) videoStatus.textContent = copy.waiting;
    updateProgress();
    void resume();
  };
  const waitForBuffer = () => hold(Math.min(...syncedVideos.map((video) => video.currentTime)));

  syncedVideos.forEach((video) => {
    video.muted = true;
    video.playsInline = true;
    for (const event of ["loadedmetadata", "loadeddata", "canplay", "seeked", "progress"]) {
      video.addEventListener(event, () => {
        if (waiting) align();
        updateProgress();
        void resume();
      });
    }
    video.addEventListener("waiting", () => {
      if (wanted && !waiting && !ready()) waitForBuffer();
    });
    video.addEventListener("error", () => {
      // Ignore an old queued error after a successful load() retry.
      if (video.error) stop(copy.failedVideo(video.getAttribute("aria-label")));
    });
    video.addEventListener("ended", () => {
      stop();
      targetTime = duration();
      align();
      updateProgress();
    });
  });
  videoProgress.addEventListener("input", () => {
    hold((Number(videoProgress.value) / 1000) * duration());
  });
  videoPlay.addEventListener("click", () => {
    if (wanted) {
      stop();
      return;
    }
    wanted = true;
    startRetries = 0;
    retryAt = 0;
    setPlaying(true);
    syncedVideos.forEach((video) => {
      video.preload = "auto";
      if (video.error || video.networkState === HTMLMediaElement.NETWORK_NO_SOURCE) video.load();
    });
    const time = waiting ? targetTime : primary.currentTime;
    hold(time >= duration() - 0.08 ? 0 : time);
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop();
  });
  const tick = () => {
    if (wanted && waiting) void resume();
    if (wanted && !waiting && !starting) {
      if (!ready()) {
        waitForBuffer();
      } else {
        for (const video of syncedVideos.slice(1)) {
          const drift = video.currentTime - primary.currentTime;
          if (Math.abs(drift) > 0.12) {
            hold();
            break;
          }
          // Small rate adjustments avoid repeated seeks for sub-frame drift.
          video.playbackRate = Math.abs(drift) > 0.025 ? (drift > 0 ? 0.96 : 1.04) : 1;
        }
      }
    }
    updateProgress();
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  updateProgress();
}

const officeExternalSlot = document.querySelector('#office-external-slot');
for (const button of document.querySelectorAll('[data-office-external]')) {
  button.addEventListener('click', () => {
    const source = button.dataset.officeExternal;
    if (!['https://office-cafe-vipe.hiwtishere.chatgpt.site/?lang=en', 'https://office-cafe-vipe.hiwtishere.chatgpt.site/shake?lang=en'].includes(source)) return;
    const frame = document.createElement('iframe');
    frame.src = source;
    frame.lang = 'en';
    frame.title = source.includes('/shake') ? 'Office Café shake experiment — English requested' : 'Office Café interactive model — English requested';
    frame.allow = 'fullscreen';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'no-referrer';
    frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-pointer-lock');
    officeExternalSlot.replaceChildren(frame);
    officeExternalSlot.hidden = false;
  });
}
