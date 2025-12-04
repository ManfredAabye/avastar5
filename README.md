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

---

## 🚀 Wichtige Änderungen in diesem Fork

- ✅ **Kompatibel mit Blender 5.0+** 
  - `imp` Modul durch `importlib` ersetzt
  - `bpy.utils.user_resource()` durch kompatible API ersetzt
  - Veraltete `bgl` Imports entfernt
- ✅ **Rückwärtskompatibel mit Blender 4.3+**
- ✅ Python 3.11+ Unterstützung
- ✅ Verbesserte `register()`-Methode & API-Anpassungen
- ✅ Ordnerstruktur und Modulnamen aktualisiert
- 🧼 Code-Bereinigung und Modernisierung

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

```
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
🔗 https://machinimatrix.org


### 🧬 Herkunft des Codes

Diese modifizierte Version von **Avastar** basiert auf einem öffentlichen Fork von  
[`jackmeeple/avastar`](https://github.com/jackmeeple/avastar), der unter der **GNU GPL v3** veröffentlicht wurde.

> Der ursprüngliche Code von Avastar stammt von [Machinimatrix](https://machinimatrix.org) und wurde später von der GitHub-Nutzerin jackmeeple als freie Open-Source-Version zur Verfügung gestellt.
> Diese Version wurde von [Manfred Aabye](https://github.com/ManfredAabye) modernisiert.
