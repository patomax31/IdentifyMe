const video = document.getElementById("video");
const canvas = document.getElementById("captureCanvas");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusText = document.getElementById("statusText");
const statusBadge = document.getElementById("statusBadge");
const usersLoaded = document.getElementById("usersLoaded");

const userName = document.getElementById("userName");
const userClass = document.getElementById("userClass");
const userAge = document.getElementById("userAge");
const userId = document.getElementById("userId");

let stream = null;
let verifyTimer = null;

function setStatus(message, state = "waiting") {
  statusText.textContent = message;
  statusBadge.textContent = message;
  statusText.className = `status ${state}`;
}

function clearUser() {
  userName.textContent = "---";
  userClass.textContent = "---";
  userAge.textContent = "---";
  userId.textContent = "---";
}

function drawToBase64() {
  const width = video.videoWidth;
  const height = video.videoHeight;
  if (!width || !height) {
    return null;
  }

  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, width, height);
  return canvas.toDataURL("image/jpeg", 0.82);
}

async function checkSystemStatus() {
  const res = await fetch("/api/login/status");
  const data = await res.json();
  usersLoaded.textContent = data.ready
    ? `${data.users_count} usuarios cargados`
    : "No hay usuarios registrados";
  return data.ready;
}

async function verifyFace() {
  const image = drawToBase64();
  if (!image) {
    return;
  }

  try {
    const res = await fetch("/api/login/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });

    const data = await res.json();
    if (!res.ok) {
      setStatus(data.message || "Error en verificacion", "error");
      return;
    }

    setStatus(data.message, data.state || "waiting");

    if (data.user) {
      userName.textContent = data.user.nombre || "---";
      userClass.textContent = data.user.salon || "---";
      userAge.textContent = data.user.edad || "---";
      userId.textContent = data.user.id != null ? `#${data.user.id}` : "---";
    } else {
      clearUser();
    }
  } catch (err) {
    setStatus("Error de red en verificacion", "error");
  }
}

async function startCamera() {
  const canStart = await checkSystemStatus();
  if (!canStart) {
    setStatus("ERROR: No hay usuarios registrados", "error");
    return;
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;

    startBtn.disabled = true;
    stopBtn.disabled = false;
    setStatus("ESPERANDO ROSTRO...", "waiting");

    if (verifyTimer) {
      clearInterval(verifyTimer);
    }
    verifyTimer = setInterval(verifyFace, 900);
  } catch (err) {
    setStatus("No se pudo acceder a la camara", "error");
  }
}

function stopCamera() {
  if (verifyTimer) {
    clearInterval(verifyTimer);
    verifyTimer = null;
  }

  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  video.srcObject = null;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  setStatus("Camara detenida", "waiting");
  clearUser();
}

startBtn.addEventListener("click", startCamera);
stopBtn.addEventListener("click", stopCamera);
window.addEventListener("beforeunload", stopCamera);
checkSystemStatus().catch(() => {
  usersLoaded.textContent = "No se pudo cargar el estado del sistema";
});
