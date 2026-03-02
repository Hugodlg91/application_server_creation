import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.java_manager import JavaManager

jm = JavaManager()
def log(msg):
    print(msg)
    
print("Début du test...")
success = jm.ensure_java(17, on_log_callback=log)
print("Succès :", success)
if success:
    print("Exe :", jm.get_java_executable(17))
