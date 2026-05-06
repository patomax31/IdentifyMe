import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Search, Filter, ScanFace, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useState } from "react";

const recognitionEvents = [
  {
    id: 1,
    user: "Ana Martínez (7A)",
    image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop",
    location: "Entrada Principal",
    timestamp: "2026-04-29 07:45:24",
    status: "authorized",
    confidence: 98.5,
    camera: "CAM-001"
  },
  {
    id: 2,
    user: "Prof. Carlos Ruiz",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
    location: "Sala de Profesores",
    timestamp: "2026-04-29 07:40:12",
    status: "authorized",
    confidence: 96.2,
    camera: "CAM-003"
  },
  {
    id: 3,
    user: "Persona Desconocida",
    image: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&h=100&fit=crop",
    location: "Entrada Principal",
    timestamp: "2026-04-29 07:37:45",
    status: "denied",
    confidence: 45.3,
    camera: "CAM-001"
  },
  {
    id: 4,
    user: "Luis Torres (9B)",
    image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop",
    location: "Biblioteca",
    timestamp: "2026-04-29 07:33:18",
    status: "authorized",
    confidence: 97.8,
    camera: "CAM-005"
  },
  {
    id: 5,
    user: "María González (8C)",
    image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop",
    location: "Laboratorio",
    timestamp: "2026-04-29 07:30:52",
    status: "authorized",
    confidence: 99.1,
    camera: "CAM-002"
  },
  {
    id: 6,
    user: "Persona Desconocida",
    image: "https://images.unsplash.com/photo-1542178243-bc20204b769f?w=100&h=100&fit=crop",
    location: "Cafetería",
    timestamp: "2026-04-29 07:25:33",
    status: "denied",
    confidence: 38.7,
    camera: "CAM-004"
  },
  {
    id: 7,
    user: "Diego Morales (7B)",
    image: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&h=100&fit=crop",
    location: "Entrada Principal",
    timestamp: "2026-04-29 07:20:21",
    status: "authorized",
    confidence: 95.4,
    camera: "CAM-001"
  },
  {
    id: 8,
    user: "Pedro Ramírez (6A)",
    image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop",
    location: "Gimnasio",
    timestamp: "2026-04-29 07:18:09",
    status: "warning",
    confidence: 72.1,
    camera: "CAM-006"
  },
];

export function RecognitionSection() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredEvents = recognitionEvents.filter(event =>
    event.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
    event.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
    event.camera.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "authorized":
        return <CheckCircle className="w-5 h-5" />;
      case "denied":
        return <XCircle className="w-5 h-5" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <ScanFace className="w-5 h-5" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      authorized: "bg-emerald-100 text-emerald-700 border-emerald-300",
      denied: "bg-red-100 text-red-700 border-red-300",
      warning: "bg-amber-100 text-amber-700 border-amber-300",
    };
    const labels = {
      authorized: "Autorizado",
      denied: "Denegado",
      warning: "Advertencia",
    };
    return (
      <Badge variant="outline" className={`${variants[status as keyof typeof variants]} px-3 py-1 font-medium`}>
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
            Eventos de Acceso
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Historial de reconocimientos
          </p>
        </div>
        <Button variant="outline" className="border-2 border-cyan-300 text-cyan-700 hover:bg-cyan-50 shadow-md text-xs px-3 h-9">
          <Filter className="w-3 h-3 mr-1" />
          Filtros
        </Button>
      </div>

      {/* Search */}
      <Card className="p-4 border-none shadow-lg">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-cyan-500" />
          <Input
            placeholder="Buscar por estudiante, ubicación o cámara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-12 h-11 border-2 border-cyan-100 focus:border-cyan-400 rounded-xl text-sm"
          />
        </div>
      </Card>

      {/* Events Grid */}
      <div className="grid grid-cols-1 gap-4">
        {filteredEvents.map((event) => (
          <Card key={event.id} className="border-none shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden">
            <div className="p-4">
              <div className="flex items-start gap-3">
                {/* User Image */}
                <div className="relative flex-shrink-0">
                  <img
                    src={event.image}
                    alt={event.user}
                    className="w-16 h-16 rounded-xl object-cover ring-2 ring-cyan-100"
                  />
                  <div className={`absolute -top-1 -right-1 w-7 h-7 rounded-lg flex items-center justify-center shadow-lg ${
                    event.status === "authorized" ? "bg-gradient-to-br from-emerald-500 to-cyan-500" :
                    event.status === "denied" ? "bg-gradient-to-br from-red-500 to-orange-500" :
                    "bg-gradient-to-br from-amber-500 to-orange-500"
                  }`}>
                    <div className="text-white scale-75">{getStatusIcon(event.status)}</div>
                  </div>
                </div>

                {/* Event Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-bold text-base text-gray-900">{event.user}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">{event.location}</p>
                    </div>
                    {getStatusBadge(event.status)}
                  </div>

                  <div className="space-y-2">
                    {/* Confidence Bar */}
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-medium text-muted-foreground">Confianza</span>
                        <span className={`text-xs font-bold ${
                          event.confidence > 90 ? "text-emerald-600" :
                          event.confidence > 70 ? "text-amber-600" :
                          "text-red-600"
                        }`}>
                          {event.confidence}%
                        </span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            event.confidence > 90 ? "bg-gradient-to-r from-emerald-500 to-cyan-500" :
                            event.confidence > 70 ? "bg-gradient-to-r from-amber-500 to-orange-500" :
                            "bg-gradient-to-r from-red-500 to-orange-500"
                          }`}
                          style={{ width: `${event.confidence}%` }}
                        />
                      </div>
                    </div>

                    {/* Info Grid */}
                    <div className="grid grid-cols-2 gap-2 pt-1">
                      <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg px-2 py-1.5">
                        <p className="text-xs text-muted-foreground mb-0.5">Cámara</p>
                        <p className="text-xs font-semibold text-gray-900">{event.camera}</p>
                      </div>
                      <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg px-2 py-1.5">
                        <p className="text-xs text-muted-foreground mb-0.5">Hora</p>
                        <p className="text-xs font-semibold text-gray-900">{event.timestamp.split(' ')[1]}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}