const video = document.getElementById("video");
const canvas = document.getElementById("captureCanvas");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const captureBtn = document.getElementById("captureBtn");
const registerStatus = document.getElementById("registerStatus");
const registerBadge = document.getElementById("registerBadge");

let stream = null;

function setRegisterStatus(message, state = "waiting") {
  registerStatus.textContent = message;
  registerBadge.textContent = message;
  registerStatus.className = `status ${state}`;
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

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });
    video.srcObject = stream;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    captureBtn.disabled = false;
    setRegisterStatus("Camara activa. Encuadra tu rostro.", "waiting");
  } catch (err) {
    setRegisterStatus("No se pudo acceder a la camara", "error");
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  video.srcObject = null;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  captureBtn.disabled = true;
  setRegisterStatus("Camara detenida", "waiting");
}

async function submitRegister() {
  const nombre = document.getElementById("nombre").value.trim();
  const grado = document.getElementById("grado").value;
  const letra = document.getElementById("letra").value.trim().toUpperCase();
  const turno = document.getElementById("turno").value;

  if (!nombre) {
    setRegisterStatus("Dato invalido. El nombre es obligatorio.", "error");
    return;
  }

  const image = drawToBase64();
  if (!image) {
    setRegisterStatus("No se pudo capturar imagen", "error");
    return;
  }

  setRegisterStatus("Procesando registro...", "positioning");

  try {
    const res = await fetch("/api/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, grado, letra, turno, image }),
    });

    const data = await res.json();
    if (!res.ok) {
      setRegisterStatus(data.message || "Error de registro", "error");
      return;
    }

    setRegisterStatus(data.message, "granted");
    document.getElementById("registerForm").reset();
  } catch (err) {
    setRegisterStatus("Error de red durante registro", "error");
  }
}

startBtn.addEventListener("click", startCamera);
stopBtn.addEventListener("click", stopCamera);
captureBtn.addEventListener("click", submitRegister);
window.addEventListener("beforeunload", stopCamera);
