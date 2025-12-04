# Avastar (modifiziert) – Blender-Addon für SL/OpenSim

Dieses Repository enthält eine **modifizierte Version von Avastar 1**, ursprünglich entwickelt von Machinimatrix, angepasst für **Blender 5.0+**.

> ⚠️ **Hinweis:** Dies ist ein nicht offizieller Fork von Avastar. Die ursprüngliche Entwicklung erfolgte durch Machinimatrix & Co. Diese Version wurde von [Manfred Aabye](https://github.com/ManfredAabye) erweitert, gewartet und aktualisiert.

---

## 🧩 Was ist Avastar?

Avastar ist ein leistungsfähiges Blender-Addon, das den Workflow für Charakter-Erstellung, Rigging und Animation für Plattformen wie **Second Life** und **OpenSimulator** vereinfacht. Es basiert auf der **SL Bento Skelett-Spezifikation** und erlaubt:

- Automatisiertes Rigging (inkl. Bento-Rigs)
- Erstellung und Export von Animationen
- Unterstützung für Devkits und Shape-Synchronisation
- Optimierter Export für .dae (Collada)

### Erweiterte Features 🔧

#### Rigging & Weights

- ✅ **Automatische Weight-Generierung** – ButtonGenerateWeights mit Island-basierter Berechnung
- ✅ **Collision Volume Tools** – Umfassende Werkzeuge für Fitted Mesh Bones
- ✅ **Mesh Deformer Support** – Experimentelle Unterstützung für Custom Mesh Deformer

#### Animation & Retargeting

- ✅ **Retargeting System** – Vollständiges Animation-Retargeting zwischen verschiedenen Rigs
- ✅ **BVH/Anim Export** – Multi-Format-Export mit Bento-Kompatibilität

#### Presets & Workflow

- ✅ **Umfangreiche Preset-Bibliothek**:
  - 7 Shape-Presets (default, big, gnome, makehuman, medium, model, etc.)
  - 3 Rig-Presets (Basic, Complete, Skeleton)
  - 3 Transfer-Presets (Belleza, ManuelLab, TMP)
  - Armature-, Binding-, Fitting-, Targetmap-Presets
- ✅ **Devkit-Integration** – Vorgefertigte Mesh-Templates (avamesh-female)

#### Performance & Upload

- ✅ **LOD-Berechnungen** – Automatische Berechnung optimaler Level-of-Detail Parameter
- ✅ **Upload-Optimierung** – Approximation von Vertex-/Triangle-Counts für SL-Upload

---

## 🚀 Wichtige Änderungen in diesem Fork

### API-Modernisierung

- ✅ **Kompatibel mit Blender 5.0+**
  - `imp` Modul durch `importlib` ersetzt
  - `bpy.utils.user_resource()` durch kompatible API ersetzt
  - Veraltete `bgl` Imports entfernt
- ✅ **Rückwärtskompatibel mit Blender 4.3+**
- ✅ Python 3.11+ Unterstützung
- ✅ Verbesserte `register()`-Methode & API-Anpassungen
- ✅ Ordnerstruktur und Modulnamen aktualisiert
- 🧼 Code-Bereinigung und Modernisierung

### Erweiterte Features & Optimierungen

- ✅ **Machinimatrix-Aufrufe entfernt** – Keine externen Benachrichtigungen oder Update-Checks
- ✅ **Erweiterte UI/UX** – Modernere Benutzeroberfläche mit besseren Tooltips
- ✅ **Bakes on Mesh (BoM) Tools** – Spezielle Tools für System Layers
- ✅ **Animesh Support** – Optimierungen für animierte Objekte
- ✅ **Verbesserte Performance** – Optimierte Algorithmen für große Meshes

---

## 🛠️ Installation

1. Dieses Repository herunterladen oder klonen
2. Ordner in `avastar` umbenennen (wenn nötig)
3. In Blender:
   - `Edit > Preferences > Add-ons`
   - `Install...` und `avastar.zip` auswählen oder direkt den Ordner
   - Add-on aktivieren

---

## 📜 Lizenz

Diese Software steht unter der **GNU General Public License v2 oder später**.

```text
Copyright (c) 2011–2015
  Magus Freston, Domino Marama, Gaia Clary (Machinimatrix)
Modifikationen (c) 2025
  Manfred Aabye
```

Siehe [LICENSE.txt](LICENSE.txt) für vollständige Lizenzdetails.

---

## 📫 Kontakt & Feedback

Fragen, Fehlerberichte oder Verbesserungsvorschläge?  
Gerne über [Issues](https://github.com/ManfredAabye/avastar/issues) oder per Fork/Pull Request!

---

## 💡 Hinweis

Dies ist keine offizielle Version von Avastar. Wenn du professionelle Unterstützung oder Lizenzen für die kommerzielle Nutzung benötigst, besuche bitte das Originalprojekt auf:  
🔗 [machinimatrix.org](https://machinimatrix.org)


### 🧬 Herkunft des Codes

Diese modifizierte Version von **Avastar** basiert auf einem öffentlichen Fork von  
[`jackmeeple/avastar`](https://github.com/jackmeeple/avastar), der unter der **GNU GPL v3** veröffentlicht wurde.

> Der ursprüngliche Code von Avastar stammt von [Machinimatrix](https://machinimatrix.org) und wurde später von der GitHub-Nutzerin jackmeeple als freie Open-Source-Version zur Verfügung gestellt.
> Diese Version wurde von [Manfred Aabye](https://github.com/ManfredAabye) modernisiert.
