import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Settings, Shield, Camera, Save } from "lucide-react";

export function SettingsSection() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
          Configuración del Sistema
        </h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Ajusta los parámetros del sistema de control de acceso escolar
        </p>
      </div>

      {/* Recognition Settings */}
      <Card className="border-none shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-cyan-500 to-blue-500 p-4">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <Camera className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-base">Configuración de Reconocimiento</h3>
              <p className="text-cyan-100 text-xs">Parámetros del motor de reconocimiento</p>
            </div>
          </div>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <Label htmlFor="confidence" className="text-sm">Nivel de Confianza Mínimo (%)</Label>
            <Input
              id="confidence"
              type="number"
              defaultValue="85"
              className="mt-2 h-10 border-2 border-cyan-100 focus:border-cyan-400 rounded-lg text-sm"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Porcentaje mínimo de confianza para autorizar acceso
            </p>
          </div>

          <div>
            <Label htmlFor="timeout" className="text-sm">Tiempo de Espera (segundos)</Label>
            <Input
              id="timeout"
              type="number"
              defaultValue="5"
              className="mt-2 h-10 border-2 border-cyan-100 focus:border-cyan-400 rounded-lg text-sm"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Tiempo máximo para completar el reconocimiento
            </p>
          </div>

          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
            <div className="space-y-0.5 flex-1">
              <Label className="text-sm">Reconocimiento Múltiple</Label>
              <p className="text-xs text-muted-foreground">
                Permitir detectar múltiples rostros simultáneamente
              </p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
            <div className="space-y-0.5 flex-1">
              <Label className="text-sm">Detección de Liveness</Label>
              <p className="text-xs text-muted-foreground">
                Verificar que el rostro es de una persona real
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>

      {/* Security Settings */}
      <Card className="border-none shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-500 to-cyan-500 p-4">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-base">Configuración de Seguridad</h3>
              <p className="text-emerald-100 text-xs">Opciones de seguridad y privacidad</p>
            </div>
          </div>
        </div>

        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
            <div className="space-y-0.5 flex-1">
              <Label className="text-sm">Autenticación de Doble Factor</Label>
              <p className="text-xs text-muted-foreground">
                Requerir PIN adicional después del reconocimiento
              </p>
            </div>
            <Switch />
          </div>

          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
            <div className="space-y-0.5 flex-1">
              <Label className="text-sm">Cifrado de Datos Biométricos</Label>
              <p className="text-xs text-muted-foreground">
                Encriptar datos de rostros almacenados
              </p>
            </div>
            <Switch defaultChecked />
          </div>

          <div>
            <Label htmlFor="retention">Retención de Imágenes (días)</Label>
            <Input 
              id="retention" 
              type="number" 
              defaultValue="30" 
              className="mt-2 h-10 border-2 border-cyan-100 focus:border-cyan-400 rounded-lg text-sm"
            />
            <p className="text-sm text-muted-foreground mt-2">
              Tiempo de almacenamiento de imágenes de reconocimiento
            </p>
          </div>

          <div className="flex items-center justify-between p-3 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-lg">
            <div className="space-y-0.5 flex-1">
              <Label className="text-sm">Registrar Intentos Fallidos</Label>
              <p className="text-xs text-muted-foreground">
                Guardar capturas de intentos de acceso denegados
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </Card>


      {/* Save Button */}
      <div className="flex justify-end">
        <Button className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-6 h-10 shadow-lg hover:shadow-xl transition-all duration-200 text-sm">
          <Save className="w-4 h-4 mr-2" />
          Guardar Configuración
        </Button>
      </div>
    </div>
  );
}