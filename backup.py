import os
import time
import subprocess
from datetime import datetime
from netmiko import ConnectHandler
import warnings

warnings.filterwarnings(action='ignore', module='.*paramiko.*')

repo = "./"

routers = [
    {'device_type': 'cisco_ios', 'ip': '192.168.1.22', 'username': 'admin', 'password': 'cisco', 'name': 'R1'},
    {'device_type': 'cisco_ios', 'ip': '10.0.5.2', 'username': 'admin', 'password': 'cisco', 'name': 'R2'},
    {'device_type': 'cisco_ios', 'ip': '10.0.5.6', 'username': 'admin', 'password': 'cisco', 'name': 'R3'}
]

def crear_carpeta(nombre):
    if not os.path.exists(nombre):
        os.makedirs(nombre)
        print(f"Carpeta lista para {nombre}")

def sacar_config(router):
    nombre = router.pop('name')
    print(f"[{nombre}] Entrando a {router['ip']} para sacar la configuración...")
    
    try:
        conexion = ConnectHandler(**router)
        config = conexion.send_command("show running-config")
        conexion.disconnect()
        router['name'] = nombre
        return config
    except Exception as e:
        print(f"[{nombre}] Falló la conexión: {e}")
        router['name'] = nombre
        return None

def hay_cambios(carpeta, config_nueva):
    archivos = os.listdir(carpeta)
    
    if not archivos:
        return True
        
    archivos.sort()
    ultimo = os.path.join(carpeta, archivos[-1])
    
    try:
        with open(ultimo, 'r') as f:
            config_vieja = f.read()
            
        if config_nueva == config_vieja:
            return False
        else:
            return True
            
    except Exception as e:
        print(f"Error al leer el archivo viejo: {e}")
        return True

def guardar_txt(carpeta, config):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archivo = f"backup_{fecha}.txt"
    ruta = os.path.join(carpeta, archivo)
    
    with open(ruta, 'w') as f:
        f.write(config)
        
    print(f"[{carpeta}] Backup guardado como {archivo}")
    return ruta

def subir_github():
    print("Sincronizando con GitHub...")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"Backup NCM Equipo 5: {fecha}"
    
    try:
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        estado = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True)
        
        if estado.stdout.strip():
            subprocess.run(["git", "commit", "-m", mensaje], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "push"], cwd=repo, check=True, capture_output=True)
            print("¡Archivos del Equipo 5 subidos a GitHub con éxito!")
        else:
            print("No hay archivos nuevos para subir a GitHub.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error al subir a GitHub: {e.stderr.decode('utf-8')}")

def main():
    print("Iniciando sistema de backups del Equipo 5...")
    print("Presiona Ctrl+C si quieres detenerlo.\n")
    
    try:
        while True:
            cambios = False
            
            for router in routers:
                nombre = router['name']
                crear_carpeta(nombre)
                
                config = sacar_config(router)
                
                if config:
                    if hay_cambios(nombre, config):
                        print(f"[{nombre}] Encontré cambios nuevos, guardando...")
                        guardar_txt(nombre, config)
                        cambios = True
                    else:
                        print(f"[{nombre}] Todo igual, no se guarda nada nuevo.")
            
            if cambios:
                subir_github()
            else:
                print("Terminó la vuelta. Nada que subir por ahora.")
                
            print("\nEsperando 5 segundos...\n")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nApagando el sistema. ¡Listo para el video!")

if __name__ == "__main__":
    main()
