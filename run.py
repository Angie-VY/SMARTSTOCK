import subprocess
import sys
import os

def main():
    print("====================================================")
    print("       SmartStock IA - Sistema de Inventarios       ")
    print("====================================================")
    print("\nIniciando el servidor de desarrollo...")
    
    # Cambiar al directorio de backend
    os.chdir('backend')
    
    # Determinar ruta del intérprete de python del venv en Windows
    python_exe = os.path.join('venv', 'Scripts', 'python.exe')
    if not os.path.exists(python_exe):
        # Fallback para sistemas Unix/Mac o si no se detecta venv
        python_exe = os.path.join('venv', 'bin', 'python')
        if not os.path.exists(python_exe):
            python_exe = 'python'  # Fallback a intérprete global
            
    print(f"[*] Usando interprete de Python: {python_exe}")
    print("[*] La API estara disponible en: http://127.0.0.1:8000/docs")
    print("[*] El Frontend SPA se abrira en: http://127.0.0.1:8000/")
    print("\n[Presiona Ctrl+C para detener el servidor]\n")
    
    ports_to_try = [8000, 8001]
    for port in ports_to_try:
        cmd = [python_exe, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port)]
        print(f"[*] Intentando iniciar el servidor en http://127.0.0.1:{port}...")
        try:
            subprocess.run(cmd, check=True)
            return
        except subprocess.CalledProcessError as e:
            print(f"\n[!] No se pudo iniciar en el puerto {port}: el puerto está ocupado o hubo un error en Uvicorn.")
            if port == ports_to_try[-1]:
                print("\n[Error] No se pudo iniciar el servidor en ningún puerto disponible.")
            else:
                print(f"[*] Intentando con el siguiente puerto disponible...\n")
        except KeyboardInterrupt:
            print("\n[!] Servidor detenido por el usuario. Hasta luego!")
            return
        except Exception as e:
            print(f"\n[!] Error al iniciar el servidor en el puerto {port}: {e}")
            if port == ports_to_try[-1]:
                print("\n[Error] No se pudo iniciar el servidor en ningún puerto disponible.")
            else:
                print(f"[*] Intentando con el siguiente puerto disponible...\n")

if __name__ == '__main__':
    main()
