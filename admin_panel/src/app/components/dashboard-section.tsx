import { Card } from "./ui/card";
import { Users, ScanFace, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart } from "recharts";

const statsData = [
  { icon: Users, label: "Estudiantes Activos", value: "847", change: "+12%", color: "from-cyan-500 to-cyan-600", bgColor: "bg-cyan-50" },
  { icon: ScanFace, label: "Accesos Hoy", value: "1,254", change: "+8%", color: "from-blue-500 to-cyan-500", bgColor: "bg-blue-50" },
  { icon: CheckCircle, label: "Ingresos Autorizados", value: "1,198", change: "+6%", color: "from-emerald-500 to-cyan-500", bgColor: "bg-emerald-50" },
  { icon: AlertTriangle, label: "Accesos Denegados", value: "56", change: "-3%", color: "from-amber-500 to-orange-500", bgColor: "bg-amber-50" },
];

const chartData = [
  { name: "Lun", reconocimientos: 450 },
  { name: "Mar", reconocimientos: 520 },
  { name: "Mié", reconocimientos: 680 },
  { name: "Jue", reconocimientos: 590 },
  { name: "Vie", reconocimientos: 740 },
  { name: "Sáb", reconocimientos: 320 },
  { name: "Dom", reconocimientos: 280 },
];

const hourlyData = [
  { hour: "00:00", accesos: 12 },
  { hour: "04:00", accesos: 8 },
  { hour: "08:00", accesos: 145 },
  { hour: "12:00", accesos: 234 },
  { hour: "16:00", accesos: 187 },
  { hour: "20:00", accesos: 98 },
];

const recentActivity = [
  { id: 1, user: "Ana Martínez (7A)", action: "Acceso autorizado", location: "Entrada Principal", time: "Hace 2 min", status: "success" },
  { id: 2, user: "Prof. Carlos Ruiz", action: "Acceso autorizado", location: "Sala de Profesores", time: "Hace 5 min", status: "success" },
  { id: 3, user: "Persona Desconocida", action: "Acceso denegado", location: "Entrada Principal", time: "Hace 8 min", status: "danger" },
  { id: 4, user: "Luis Torres (9B)", action: "Acceso autorizado", location: "Biblioteca", time: "Hace 12 min", status: "success" },
  { id: 5, user: "María González (8C)", action: "Acceso autorizado", location: "Laboratorio", time: "Hace 15 min", status: "success" },
];

export function DashboardSection() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
          Dashboard
        </h2>
        <p className="text-muted-foreground mt-1 text-sm">Panel de Control Escolar</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        {statsData.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="relative overflow-hidden border-none shadow-lg hover:shadow-xl transition-all duration-300">
              <div className={`absolute inset-0 opacity-5 bg-gradient-to-br ${stat.color}`} />
              <div className="p-3 relative">
                <div className="flex items-start justify-between mb-2">
                  <div className={`w-10 h-10 ${stat.bgColor} rounded-xl flex items-center justify-center shadow-md`}>
                    <div className={`w-8 h-8 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center`}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-lg">
                    <TrendingUp className="w-3 h-3" />
                    <span className="text-xs font-semibold">{stat.change}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mb-0.5">{stat.label}</p>
                <p className="text-xl font-bold bg-gradient-to-br from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  {stat.value}
                </p>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-4">
        <Card className="p-4 border-none shadow-lg">
          <div className="mb-4">
            <h3 className="text-base font-semibold">Accesos por Día</h3>
            <p className="text-xs text-muted-foreground mt-1">Últimos 7 días</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={1} />
                  <stop offset="100%" stopColor="#0891b2" stopOpacity={0.8} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0f2fe" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
                }}
                cursor={{ fill: 'rgba(6, 182, 212, 0.05)' }}
              />
              <Bar dataKey="reconocimientos" fill="url(#barGradient)" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-4 border-none shadow-lg">
          <div className="mb-4">
            <h3 className="text-base font-semibold">Accesos por Hora</h3>
            <p className="text-xs text-muted-foreground mt-1">Actividad de hoy</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={hourlyData}>
              <defs>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0f2fe" vertical={false} />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
                }}
              />
              <Area type="monotone" dataKey="accesos" stroke="#06b6d4" strokeWidth={3} fill="url(#areaGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-4 border-none shadow-lg">
        <div className="mb-3">
          <h3 className="text-base font-semibold">Actividad Reciente</h3>
          <p className="text-xs text-muted-foreground mt-1">Últimos eventos registrados</p>
        </div>
        <div className="space-y-2">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg hover:shadow-md transition-all duration-200 border border-cyan-100/50">
              <div className="flex items-center gap-2">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center shadow-md ${
                  activity.status === "success"
                    ? "bg-gradient-to-br from-cyan-500 to-blue-500"
                    : "bg-gradient-to-br from-amber-500 to-orange-500"
                }`}>
                  <ScanFace className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">{activity.user}</p>
                  <p className="text-xs text-muted-foreground">{activity.location}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground mb-1">{activity.time}</p>
                <span className={`text-xs px-2 py-1 rounded-md font-medium ${
                  activity.status === "success"
                    ? "bg-emerald-100 text-emerald-700 border border-emerald-200"
                    : "bg-amber-100 text-amber-700 border border-amber-200"
                }`}>
                  {activity.status === "success" ? "OK" : "No"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}