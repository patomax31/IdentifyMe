/* ═══════════════════════════════════════════════════════════════════════════
   IdentifyMe · app.js
   Drawer, navegación de vistas, reloj, tabs admin
═══════════════════════════════════════════════════════════════════════════ */

// ── Drawer ────────────────────────────────────────────────────────────────
const drawer        = document.getElementById('drawer');
const drawerOverlay = document.getElementById('drawerOverlay');
const hamburger     = document.getElementById('hamburger');
const drawerClose   = document.getElementById('drawerClose');

function openDrawer() {
  drawer.classList.add('open');
  drawerOverlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeDrawer() {
  drawer.classList.remove('open');
  drawerOverlay.classList.remove('open');
  document.body.style.overflow = '';
}

hamburger?.addEventListener('click', openDrawer);
drawerClose?.addEventListener('click', closeDrawer);
drawerOverlay?.addEventListener('click', closeDrawer);

// Cerrar con Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeDrawer();
});

// ── Navegación entre vistas ───────────────────────────────────────────────
const navBtns = document.querySelectorAll('.nav-btn[data-view]');
const views   = document.querySelectorAll('.view');

function showView(viewId) {
  views.forEach(v => v.classList.add('hidden'));
  navBtns.forEach(b => b.classList.remove('active'));

  const target = document.getElementById(`view-${viewId}`);
  if (target) target.classList.remove('hidden');

  const activeBtn = document.querySelector(`.nav-btn[data-view="${viewId}"]`);
  if (activeBtn) activeBtn.classList.add('active');

  closeDrawer();
}

navBtns.forEach(btn => {
  btn.addEventListener('click', () => showView(btn.dataset.view));
});

// ── Reloj en tiempo real ──────────────────────────────────────────────────
const clockH = document.getElementById('clockH');
const clockD = document.getElementById('clockD');

function updateClock() {
  const now  = new Date();
  const hhmm = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
  const date = now.toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short' });

  if (clockH) clockH.textContent = hhmm;
  if (clockD) clockD.textContent = date.replace(/\./g, '').replace(/,/g, '');
}

updateClock();
setInterval(updateClock, 1000);

// ── Tabs del panel admin ──────────────────────────────────────────────────
const tabBtns  = document.querySelectorAll('.tab-btn[data-admin-tab]');
const adminTabs = document.querySelectorAll('.admin-tab');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.adminTab;

    tabBtns.forEach(b   => b.classList.remove('active'));
    adminTabs.forEach(t => t.classList.add('hidden'));

    btn.classList.add('active');
    const el = document.getElementById(`admin-${target}`);
    if (el) el.classList.remove('hidden');
  });
});

// ── Logout ────────────────────────────────────────────────────────────────
document.getElementById('logoutBtn')?.addEventListener('click', async () => {
  try {
    await fetch('/api/admin/logout', { method: 'POST' });
  } catch (_) {}
  window.location.href = '/';
});

// ── Estado del sistema (sidebar) ──────────────────────────────────────────
async function fetchSystemStatus() {
  const el = document.getElementById('systemStatus');
  if (!el) return;
  try {
    const res  = await fetch('/api/login/status');
    const data = await res.json();
    el.textContent = data.ready
      ? `✓ ${data.users_count} usuarios cargados`
      : (data.message || 'Sin usuarios registrados');
  } catch (_) {
    el.textContent = 'Sin conexión al servidor';
  }
}

fetchSystemStatus();

// ── Stats del home ────────────────────────────────────────────────────────
async function fetchHomeStats() {
  try {
    const res  = await fetch('/api/admin/students');
    const data = await res.json();
    const list = data.students || data || [];

    const total   = document.getElementById('statTotal');
    const activos = document.getElementById('statActivos');
    if (total)   total.textContent   = list.length;
    if (activos) activos.textContent = list.filter(s => s.activo !== false).length;
  } catch (_) {}
}

fetchHomeStats();

// ── Cámara: Login ─────────────────────────────────────────────────────────
let loginStream    = null;
let loginInterval  = null;

const loginVideo   = document.getElementById('loginVideo');
const loginCanvas  = document.getElementById('loginCanvas');
const loginStart   = document.getElementById('loginStart');
const loginStop    = document.getElementById('loginStop');
const loginMessage = document.getElementById('loginMessage');

const loginFields = {
  name:  document.getElementById('loginUserName'),
  cls:   document.getElementById('loginUserClass'),
  age:   document.getElementById('loginUserAge'),
  id:    document.getElementById('loginUserId'),
};

function resetLoginUser() {
  if (loginFields.name) loginFields.name.textContent = '---';
  if (loginFields.cls)  loginFields.cls.textContent  = '---';
  if (loginFields.age)  loginFields.age.textContent  = '---';
  if (loginFields.id)   loginFields.id.textContent   = '---';
}

async function captureAndVerify() {
  if (!loginVideo || !loginCanvas) return;
  loginCanvas.width  = loginVideo.videoWidth;
  loginCanvas.height = loginVideo.videoHeight;
  loginCanvas.getContext('2d').drawImage(loginVideo, 0, 0);
  const image = loginCanvas.toDataURL('image/jpeg', 0.8);

  try {
    const res  = await fetch('/api/login/verify', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ image }),
    });
    const data = await res.json();

    if (loginMessage) {
      loginMessage.textContent  = data.message || '';
      loginMessage.className    = `feedback ${data.state || ''}`;
    }

    if (data.state === 'granted' && data.user) {
      if (loginFields.name) loginFields.name.textContent = data.user.nombre || '---';
      if (loginFields.cls)  loginFields.cls.textContent  = data.user.salon  || '---';
      if (loginFields.age)  loginFields.age.textContent  = data.user.edad   || '---';
      if (loginFields.id)   loginFields.id.textContent   = `#${data.user.id}` || '---';
    } else {
      resetLoginUser();
    }
  } catch (_) {}
}

loginStart?.addEventListener('click', async () => {
  try {
    loginStream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (loginVideo) loginVideo.srcObject = loginStream;
    loginStart.disabled = true;
    loginStop.disabled  = false;
    loginInterval = setInterval(captureAndVerify, 1200);
  } catch (e) {
    if (loginMessage) loginMessage.textContent = 'No se pudo acceder a la cámara.';
  }
});

loginStop?.addEventListener('click', () => {
  clearInterval(loginInterval);
  if (loginStream) loginStream.getTracks().forEach(t => t.stop());
  loginStream = null;
  if (loginVideo) loginVideo.srcObject = null;
  loginStart.disabled = false;
  loginStop.disabled  = true;
  if (loginMessage) {
    loginMessage.textContent = 'ESPERANDO ROSTRO...';
    loginMessage.className   = 'feedback';
  }
  resetLoginUser();
});

// ── Cámara: Register ──────────────────────────────────────────────────────
let regStream = null;

const regVideo   = document.getElementById('regVideo');
const regCanvas  = document.getElementById('regCanvas');
const regStart   = document.getElementById('regStart');
const regCapture = document.getElementById('regCapture');
const regStop    = document.getElementById('regStop');
const regMessage = document.getElementById('regMessage');

regStart?.addEventListener('click', async () => {
  try {
    regStream = await navigator.mediaDevices.getUserMedia({ video: true });
    if (regVideo) regVideo.srcObject = regStream;
    regStart.disabled   = true;
    regCapture.disabled = false;
    regStop.disabled    = false;
  } catch (_) {
    if (regMessage) regMessage.textContent = 'No se pudo acceder a la cámara.';
  }
});

regCapture?.addEventListener('click', async () => {
  if (!regVideo || !regCanvas) return;

  const nombre = document.getElementById('regNombre')?.value.trim();
  const grado  = document.getElementById('regGrado')?.value;
  const letra  = document.getElementById('regLetra')?.value.trim().toUpperCase();
  const turno  = document.getElementById('regTurno')?.value;

  if (!nombre || !letra) {
    if (regMessage) regMessage.textContent = 'Completa nombre y grupo antes de capturar.';
    return;
  }

  regCanvas.width  = regVideo.videoWidth;
  regCanvas.height = regVideo.videoHeight;
  regCanvas.getContext('2d').drawImage(regVideo, 0, 0);
  const image = regCanvas.toDataURL('image/jpeg', 0.85);

  if (regMessage) regMessage.textContent = 'Procesando...';

  try {
    const res  = await fetch('/api/registro', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ nombre, grado, letra, turno, image }),
    });
    const data = await res.json();
    if (regMessage) regMessage.textContent = data.message || (data.ok ? '¡Registrado!' : 'Error');
  } catch (_) {
    if (regMessage) regMessage.textContent = 'Error de conexión.';
  }
});

regStop?.addEventListener('click', () => {
  if (regStream) regStream.getTracks().forEach(t => t.stop());
  regStream = null;
  if (regVideo) regVideo.srcObject = null;
  regStart.disabled   = false;
  regCapture.disabled = true;
  regStop.disabled    = true;
});

// ── Admin: tabla de estudiantes ───────────────────────────────────────────
async function loadStudents() {
  const tbody = document.querySelector('#studentsTable tbody');
  const msg   = document.getElementById('admStudentsMsg');
  if (!tbody) return;
  try {
    const res   = await fetch('/api/admin/students');
    const data  = await res.json();
    const list  = data.students || data || [];
    tbody.innerHTML = list.map(s => `
      <tr>
        <td>${s.id}</td>
        <td>${s.nombre}</td>
        <td>${s.grado}</td>
        <td>${s.letra}</td>
        <td>${s.turno}</td>
        <td>${s.activo !== false ? '✅' : '❌'}</td>
        <td>
          <button style="padding:4px 10px;font-size:0.75rem"
            onclick="deleteStudent(${s.id})">Eliminar</button>
        </td>
      </tr>`).join('');
    if (msg) msg.textContent = `${list.length} estudiantes encontrados.`;
  } catch (_) {
    if (msg) msg.textContent = 'Error al cargar estudiantes.';
  }
}

window.deleteStudent = async (id) => {
  if (!confirm(`¿Eliminar estudiante #${id}?`)) return;
  try {
    await fetch(`/api/admin/students/${id}`, { method: 'DELETE' });
    loadStudents();
  } catch (_) {}
};

document.getElementById('admRefresh')?.addEventListener('click', loadStudents);

document.getElementById('admCreate')?.addEventListener('click', async () => {
  const msg    = document.getElementById('admStudentsMsg');
  const nombre = document.getElementById('admNombre')?.value.trim();
  const grado  = document.getElementById('admGrado')?.value;
  const letra  = document.getElementById('admGrupo')?.value.trim().toUpperCase();
  const turno  = document.getElementById('admTurno')?.value;

  if (!nombre || !letra) {
    if (msg) msg.textContent = 'Completa nombre y grupo.';
    return;
  }
  try {
    const res  = await fetch('/api/admin/students', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ nombre, grado, letra, turno }),
    });
    const data = await res.json();
    if (msg) msg.textContent = data.message || (data.ok ? 'Creado.' : 'Error');
    if (data.ok) loadStudents();
  } catch (_) {
    if (msg) msg.textContent = 'Error de conexión.';
  }
});

// ── Admin: configuración del modelo ──────────────────────────────────────
document.getElementById('cfgLoad')?.addEventListener('click', async () => {
  try {
    const res  = await fetch('/api/admin/config');
    const data = await res.json();
    if (data.scale)     document.getElementById('cfgScale').value     = data.scale;
    if (data.tolerance) document.getElementById('cfgTolerance').value = data.tolerance;
    if (data.cooldown)  document.getElementById('cfgCooldown').value  = data.cooldown;
    const msg = document.getElementById('cfgMsg');
    if (msg) msg.textContent = 'Configuración cargada.';
  } catch (_) {}
});

document.getElementById('cfgSave')?.addEventListener('click', async () => {
  const msg = document.getElementById('cfgMsg');
  try {
    const res  = await fetch('/api/admin/config', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        scale:     parseFloat(document.getElementById('cfgScale')?.value),
        tolerance: parseFloat(document.getElementById('cfgTolerance')?.value),
        cooldown:  parseFloat(document.getElementById('cfgCooldown')?.value),
      }),
    });
    const data = await res.json();
    if (msg) msg.textContent = data.message || (data.ok ? 'Guardado.' : 'Error');
  } catch (_) {
    if (msg) msg.textContent = 'Error de conexión.';
  }
});

// ── Admin: administradores ────────────────────────────────────────────────
async function loadAdmins() {
  const tbody = document.querySelector('#adminsTable tbody');
  const msg   = document.getElementById('adminMsg');
  if (!tbody) return;
  try {
    const res  = await fetch('/api/admin/admins');
    const data = await res.json();
    const list = data.admins || data || [];
    tbody.innerHTML = list.map(a => `
      <tr>
        <td>${a.id}</td>
        <td>${a.numero_empleado}</td>
        <td>${a.nombre}</td>
        <td>${a.rol}</td>
        <td>${a.correo || '---'}</td>
        <td>${a.activo !== false ? '✅' : '❌'}</td>
      </tr>`).join('');
    if (msg) msg.textContent = `${list.length} administradores.`;
  } catch (_) {}
}

document.getElementById('adminRefresh')?.addEventListener('click', loadAdmins);

document.getElementById('adminCreate')?.addEventListener('click', async () => {
  const msg = document.getElementById('adminMsg');
  const body = {
    numero_empleado: document.getElementById('adminNum')?.value.trim(),
    nombre:          document.getElementById('adminNombre')?.value.trim(),
    rol:             document.getElementById('adminRol')?.value.trim(),
    correo:          document.getElementById('adminCorreo')?.value.trim(),
    password:        document.getElementById('adminPass')?.value,
  };
  if (!body.numero_empleado || !body.nombre || !body.password) {
    if (msg) msg.textContent = 'Completa los campos obligatorios.';
    return;
  }
  try {
    const res  = await fetch('/api/admin/admins', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(body),
    });
    const data = await res.json();
    if (msg) msg.textContent = data.message || (data.ok ? 'Admin creado.' : 'Error');
    if (data.ok) loadAdmins();
  } catch (_) {
    if (msg) msg.textContent = 'Error de conexión.';
  }
});