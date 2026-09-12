# Taller MBA UC —  agente airbnb

Esto es una referencia para el taller. **No hay ningun sistema hecho aca**: hay algunos datos para agilizar partes del desarrollo propuesto, el framework para seguir las guías de desarrollo, y una skill que te ayuda a decidir el diseno antes de escribir codigo.

| Archivo | Que es |
|---|---|
| `marco-de-agentes.md` | El framework acá. Trae una plantilla para seguir el diseño y un ejemplo de como se ve completada. |
| `supuestos.yaml` | Tarifa y ocupacion por tipologia con estacionalidad de 12 meses, gastos comunes, costos de operacion, equipamiento y parametros del credito. Son una **referencia**, ejemplo para completar datos en la sección del evaluador financiero. |
| `skills/entrevistador-de-diseno/` | Una skill que entrevista al usuario hasta que el diseno queda cerrado. |

---

## 1. Abri la terminal

| | Como |
|---|---|
| **Mac** | `Cmd + Espacio`, escribi **Terminal**, Enter |
| **Windows** | Tecla Windows, escribi **PowerShell**, Enter |

## 2. Verifica que tenes lo necesario

| | Mac | Windows |
|---|---|---|
| Git | `git --version` | `git --version` |
| Python | `python3 --version` | `python --version` |

Los dos tienen que responder con un numero de version. Si alguno dice *command not
found* o *no se reconoce*, instalalo antes de seguir: Git en
[git-scm.com](https://git-scm.com), Python en [python.org](https://python.org).

> **Windows:** al instalar Python, marca la casilla **"Add Python to PATH"** en la
> primera pantalla del instalador. Si no la marcas, `python` no va a responder y vas
> a tener que reinstalar.

## 3. Baja los archivos

Igual en los dos sistemas. Parate en la carpeta donde quieras trabajar y corre:

```
git clone https://github.com/bnavoni/taller-mba-uc.git
cd taller-mba-uc
```

## 4. Instala la skill

Aca **si** cambia segun el sistema. La skill es una carpeta que tiene que quedar
dentro de `.claude/skills/` de tu proyecto.

**Mac**
```
mkdir -p .claude/skills
cp -R skills/entrevistador-de-diseno .claude/skills/
```

**Windows (PowerShell)**
```
New-Item -ItemType Directory -Force .claude\skills | Out-Null
Copy-Item -Recurse skills\entrevistador-de-diseno .claude\skills\
```

Para confirmar que quedo, abri Claude Code en esta carpeta y pedile que liste las
skills que tiene cargadas.

## 5. Arranca, seguí los pasos propuestos

```
claude
```

En la terminal, o abri el Claude Code de escritorio.
