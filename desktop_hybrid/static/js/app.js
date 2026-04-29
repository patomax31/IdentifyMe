const state = {
  view: "home",
  login: { stream: null, timer: null },
  register: { stream: null },
  drawerOpen: false,
};

function $(id) {
  return document.getElementById(id);
}

function setSystemStatus(msg) {
  $("systemStatus").textContent = msg;
}

function setDrawer(open) {
  state.drawerOpen = open;
  $("sidebar").classList.toggle("open", open);
  $("overlay").classList.toggle("hidden", !open);
}

function toggleDrawer() {
  setDrawer(!state.drawerOpen);
}

function showView(name) {
  document.querySelectorAll(".view").forEach((el) => el.classList.add("hidden"));
  $(`view-${name}`).classList.remove("hidden");
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelector(`.nav-btn[data-view='${name}']`).classList.add("active");
  state.view = name;

  const statusMap = {
    home: "Dashboard institucional listo.",
    login: "Acceso facial activo.",
    register: "Registro biometrico disponible.",
    admin: "Panel administrativo listo.",
  };
  setSystemStatus(statusMap[name] || "VerifyMe listo.");
}

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.message || `HTTP ${response.status}`);
  }
  return data;
}

function drawVideoToCanvas(videoEl, canvasEl) {
  if (!videoEl.videoWidth || !videoEl.videoHeight) return null;
  canvasEl.width = videoEl.videoWidth;
  canvasEl.height = videoEl.videoHeight;
  const ctx = canvasEl.getContext("2d");
  ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
  return canvasEl.toDataURL("image/jpeg", 0.82);
}

function stopLoginCamera() {
  if (state.login.timer) {
    clearInterval(state.login.timer);
    state.login.timer = null;
  }
  if (state.login.stream) {
    state.login.stream.getTracks().forEach((t) => t.stop());
    state.login.stream = null;
  }
  $("loginVideo").srcObject = null;
  $("loginStart").disabled = false;
  $("loginStop").disabled = true;
}

function clearLoginUser() {
  $("loginUserName").textContent = "---";
  $("loginUserClass").textContent = "---";
  $("loginUserAge").textContent = "---";
  $("loginUserId").textContent = "---";
}

async function verifyLoginFrame() {
  const image = drawVideoToCanvas($("loginVideo"), $("loginCanvas"));
  if (!image) return;

  try {
    const data = await jsonFetch("/api/login/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });

    $("loginMessage").textContent = data.message;
    if (data.user) {
      $("loginUserName").textContent = data.user.nombre || "---";
      $("loginUserClass").textContent = data.user.salon || "---";
      $("loginUserAge").textContent = data.user.edad || "---";
      $("loginUserId").textContent = data.user.id != null ? `#${data.user.id}` : "---";
    } else {
      clearLoginUser();
    }
  } catch (error) {
    $("loginMessage").textContent = error.message;
  }
}

async function startLoginCamera() {
  try {
    const status = await jsonFetch("/api/login/status");
    if (!status.ready) {
      $("loginMessage").textContent = status.message || "No listo";
      return;
    }

    state.login.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    $("loginVideo").srcObject = state.login.stream;
    $("loginStart").disabled = true;
    $("loginStop").disabled = false;
    $("loginMessage").textContent = "ESPERANDO ROSTRO...";

    if (state.login.timer) clearInterval(state.login.timer);
    state.login.timer = setInterval(verifyLoginFrame, 900);
  } catch (error) {
    $("loginMessage").textContent = error.message;
  }
}

function stopRegisterCamera() {
  if (state.register.stream) {
    state.register.stream.getTracks().forEach((t) => t.stop());
    state.register.stream = null;
  }
  $("regVideo").srcObject = null;
  $("regStart").disabled = false;
  $("regStop").disabled = true;
}

async function startRegisterCamera() {
  try {
    state.register.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    $("regVideo").srcObject = state.register.stream;
    $("regStart").disabled = true;
    $("regStop").disabled = false;
    $("regMessage").textContent = "Camara activa. Encuadra tu rostro.";
  } catch (error) {
    $("regMessage").textContent = error.message;
  }
}

async function captureAndRegister() {
  const image = drawVideoToCanvas($("regVideo"), $("regCanvas"));
  if (!image) {
    $("regMessage").textContent = "No se pudo capturar imagen";
    return;
  }

  const payload = {
    nombre: $("regNombre").value.trim(),
    grado: $("regGrado").value,
    letra: $("regLetra").value.trim().toUpperCase(),
    turno: $("regTurno").value,
    image,
  };

  try {
    const data = await jsonFetch("/api/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("regMessage").textContent = data.message;
  } catch (error) {
    $("regMessage").textContent = error.message;
  }
}

function setAdminTab(name) {
  document.querySelectorAll(".admin-tab").forEach((tab) => tab.classList.add("hidden"));
  $(`admin-${name}`).classList.remove("hidden");
  document.querySelectorAll(".tab-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelector(`.tab-btn[data-admin-tab='${name}']`).classList.add("active");
}

function studentsRowsHtml(students) {
  return students.map((s) => `
    <tr>
      <td>${s.id}</td>
      <td>${s.nombre}</td>
      <td>${s.grado}</td>
      <td>${s.grupo}</td>
      <td>${s.turno}</td>
      <td>${s.estado_activo ? "Activo" : "Inactivo"}</td>
      <td>
        <small class="action-link" onclick="window.editStudent(${s.id}, '${s.nombre.replace(/'/g, "\\'")}', '${s.grado}', '${s.grupo}', '${s.turno}', ${s.estado_activo})">Editar</small>
        &nbsp;|&nbsp;
        <small class="action-link danger" onclick="window.deleteStudent(${s.id})">Desactivar</small>
      </td>
    </tr>
  `).join("");
}

async function loadStudents() {
  try {
    const data = await jsonFetch("/api/admin/students");
    $("studentsTable").querySelector("tbody").innerHTML = studentsRowsHtml(data.students);
  } catch (error) {
    $("admStudentsMsg").textContent = error.message;
  }
}

async function createStudent() {
  const payload = {
    nombre: $("admNombre").value.trim(),
    grado: $("admGrado").value,
    grupo: $("admGrupo").value.trim().toUpperCase(),
    turno: $("admTurno").value,
  };

  try {
    const data = await jsonFetch("/api/admin/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("admStudentsMsg").textContent = data.message;
    await loadStudents();
  } catch (error) {
    $("admStudentsMsg").textContent = error.message;
  }
}

window.editStudent = async function (id, nombre, grado, grupo, turno, estado) {
  const newNombre = prompt("Nombre", nombre);
  if (!newNombre) return;
  const payload = {
    nombre: newNombre,
    grado,
    grupo,
    turno,
    estado_activo: estado,
  };

  try {
    const data = await jsonFetch(`/api/admin/students/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("admStudentsMsg").textContent = data.message;
    await loadStudents();
  } catch (error) {
    $("admStudentsMsg").textContent = error.message;
  }
};

window.deleteStudent = async function (id) {
  if (!confirm("Desactivar estudiante?")) return;
  try {
    const data = await jsonFetch(`/api/admin/students/${id}`, { method: "DELETE" });
    $("admStudentsMsg").textContent = data.message;
    await loadStudents();
  } catch (error) {
    $("admStudentsMsg").textContent = error.message;
  }
};

async function loadModelConfig() {
  try {
    const data = await jsonFetch("/api/admin/model-config");
    $("cfgScale").value = data.config.scale;
    $("cfgTolerance").value = data.config.tolerance;
    $("cfgCooldown").value = data.config.cooldown_seconds;
    $("cfgMsg").textContent = "Configuracion cargada.";
  } catch (error) {
    $("cfgMsg").textContent = error.message;
  }
}

async function saveModelConfig() {
  const payload = {
    scale: Number($("cfgScale").value),
    tolerance: Number($("cfgTolerance").value),
    cooldown_seconds: Number($("cfgCooldown").value),
  };

  try {
    const data = await jsonFetch("/api/admin/model-config", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("cfgMsg").textContent = data.message;
  } catch (error) {
    $("cfgMsg").textContent = error.message;
  }
}

function adminsRowsHtml(admins) {
  return admins.map((a) => `
    <tr>
      <td>${a.id}</td>
      <td>${a.num_empleado}</td>
      <td>${a.nombre_completo}</td>
      <td>${a.rol}</td>
      <td>${a.correo}</td>
      <td>${a.estado_activo ? "Activo" : "Inactivo"}</td>
    </tr>
  `).join("");
}

async function loadAdmins() {
  try {
    const data = await jsonFetch("/api/admin/admins");
    $("adminsTable").querySelector("tbody").innerHTML = adminsRowsHtml(data.admins);
  } catch (error) {
    $("adminMsg").textContent = error.message;
  }
}

async function createAdmin() {
  const payload = {
    num_empleado: $("adminNum").value.trim(),
    nombre_completo: $("adminNombre").value.trim(),
    rol: $("adminRol").value.trim(),
    correo: $("adminCorreo").value.trim(),
    password: $("adminPass").value,
  };

  try {
    const data = await jsonFetch("/api/admin/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("adminMsg").textContent = data.message;
    await loadAdmins();
  } catch (error) {
    $("adminMsg").textContent = error.message;
  }
}

async function bootstrap() {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      showView(btn.dataset.view);
      if (window.matchMedia("(max-width: 720px)").matches) {
        setDrawer(false);
      }
    });
  });

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => setAdminTab(btn.dataset.adminTab));
  });

  $("hamburger").addEventListener("click", toggleDrawer);
  $("closeDrawer").addEventListener("click", () => setDrawer(false));
  $("overlay").addEventListener("click", () => setDrawer(false));

  $("loginStart").addEventListener("click", startLoginCamera);
  $("loginStop").addEventListener("click", stopLoginCamera);

  $("regStart").addEventListener("click", startRegisterCamera);
  $("regStop").addEventListener("click", stopRegisterCamera);
  $("regCapture").addEventListener("click", captureAndRegister);

  $("admCreate").addEventListener("click", createStudent);
  $("admRefresh").addEventListener("click", loadStudents);

  $("cfgLoad").addEventListener("click", loadModelConfig);
  $("cfgSave").addEventListener("click", saveModelConfig);

  $("adminCreate").addEventListener("click", createAdmin);
  $("adminRefresh").addEventListener("click", loadAdmins);

  try {
    const data = await jsonFetch("/status");
    setSystemStatus(data.message);
  } catch (error) {
    setSystemStatus(error.message);
  }

  showView("home");
  setDrawer(false);

  if (window.lucide) {
    window.lucide.createIcons();
  }

  await Promise.all([loadStudents(), loadModelConfig(), loadAdmins()]);
}

window.addEventListener("beforeunload", () => {
  stopLoginCamera();
  stopRegisterCamera();
});

window.addEventListener("DOMContentLoaded", bootstrap);
