import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Search, UserPlus, MoreVertical, CheckCircle, XCircle } from "lucide-react";
import { useState } from "react";

const usersData = [
  { id: 1, name: "Ana Martínez", email: "ana.martinez@escuela.edu", department: "7° A", status: "active", lastAccess: "Hace 2 min", image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop" },
  { id: 2, name: "Prof. Carlos Ruiz", email: "carlos.ruiz@escuela.edu", department: "Matemáticas", status: "active", lastAccess: "Hace 5 min", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop" },
  { id: 3, name: "Luis Torres", email: "luis.torres@escuela.edu", department: "9° B", status: "active", lastAccess: "Hace 12 min", image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop" },
  { id: 4, name: "María González", email: "maria.gonzalez@escuela.edu", department: "8° C", status: "active", lastAccess: "Hace 15 min", image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop" },
  { id: 5, name: "Pedro Ramírez", email: "pedro.ramirez@escuela.edu", department: "6° A", status: "inactive", lastAccess: "Hace 2 días", image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop" },
  { id: 6, name: "Prof. Laura Sánchez", email: "laura.sanchez@escuela.edu", department: "Ciencias", status: "active", lastAccess: "Hace 1 hora", image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop" },
  { id: 7, name: "Diego Morales", email: "diego.morales@escuela.edu", department: "7° B", status: "active", lastAccess: "Hace 30 min", image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&h=100&fit=crop" },
  { id: 8, name: "Sofia Castro", email: "sofia.castro@escuela.edu", department: "8° A", status: "active", lastAccess: "Hace 45 min", image: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop" },
];

export function UsersSection() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredUsers = usersData.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
            Estudiantes y Personal
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">
            {usersData.length} usuarios registrados
          </p>
        </div>
        <Button className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 text-sm px-3">
          <UserPlus className="w-4 h-4 mr-1" />
          Nuevo
        </Button>
      </div>

      {/* Search */}
      <Card className="p-4 border-none shadow-lg">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-cyan-500" />
          <Input
            placeholder="Buscar por nombre, email o grado..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-12 h-11 border-2 border-cyan-100 focus:border-cyan-400 rounded-xl text-sm"
          />
        </div>
      </Card>

      {/* Users Table */}
      <Card className="border-none shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-cyan-50 to-blue-50 border-b-2 border-cyan-200">
              <tr>
                <th className="text-left p-3 font-semibold text-gray-700 text-sm">Usuario</th>
                <th className="text-left p-3 font-semibold text-gray-700 text-sm">Grado/Rol</th>
                <th className="text-left p-3 font-semibold text-gray-700 text-sm">Estado</th>
                <th className="text-left p-3 font-semibold text-gray-700 text-sm">Último Acceso</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b border-cyan-50 hover:bg-gradient-to-r hover:from-cyan-50/50 hover:to-blue-50/50 transition-all duration-200">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="relative">
                        <img
                          src={user.image}
                          alt={user.name}
                          className="w-9 h-9 rounded-lg object-cover ring-2 ring-cyan-100"
                        />
                        <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${
                          user.status === "active" ? "bg-emerald-500" : "bg-gray-400"
                        }`} />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 text-sm">{user.name}</p>
                        <p className="text-xs text-muted-foreground">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-3">
                    <Badge variant="outline" className="border-cyan-300 text-cyan-700 bg-cyan-50 px-2 py-0.5 text-xs">
                      {user.department}
                    </Badge>
                  </td>
                  <td className="p-3">
                    {user.status === "active" ? (
                      <div className="flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                        <span className="text-xs font-medium text-emerald-600">Activo</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />
                        <span className="text-xs font-medium text-gray-500">Inactivo</span>
                      </div>
                    )}
                  </td>
                  <td className="p-3 text-xs text-muted-foreground">{user.lastAccess}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}