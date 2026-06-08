# resources/images.py
import os
from kivy.core.image import Image as CoreImage
from kivy.resources import resource_find

class ImageManager:
    """
    Gestor simple de imágenes para el proyecto.
    - resolve_image(file_name): devuelve ruta absoluta si existe, o None.
    - load_image(file_name): devuelve un CoreImage (cacheado) o None.
    - clear_cache(): limpia el cache.
    """

    def __init__(self):
        pkg_dir = os.path.dirname(os.path.abspath(__file__))  # .../resources
        project_root = os.path.dirname(pkg_dir)
        self.resources_images = os.path.join(project_root, "resources", "images")
        # rutas adicionales donde buscar (icons, root)
        self.resources_icons = os.path.join(self.resources_images, "icons")
        self.project_root = project_root
        self._cache = {}

    def _candidates(self, file_name):
        # Genera rutas candidatas en orden de preferencia
        yield os.path.join(self.resources_images, file_name)
        yield os.path.join(self.resources_icons, file_name)
        # buscar variantes @2x/@3x
        name, ext = os.path.splitext(file_name)
        yield os.path.join(self.resources_images, f"{name}@2x{ext}")
        yield os.path.join(self.resources_images, f"{name}@3x{ext}")
        # fallback a la raíz del proyecto (para archivos especiales)
        yield os.path.join(self.project_root, file_name)
        # por último, intentar resource_find (Kivy resource path)
        found = resource_find(file_name)
        if found:
            yield found

    def resolve_image(self, file_name):
        """
        Devuelve la primera ruta existente o None.
        """
        if not file_name:
            return None
        for p in self._candidates(file_name):
            try:
                if p and os.path.exists(p):
                    return p
            except Exception:
                continue
        return None

    def load_image(self, file_name):
        """
        Devuelve un CoreImage (cacheado) o None si no se encuentra.
        """
        if not file_name:
            return None
        # Si ya está en cache, devolver
        if file_name in self._cache:
            return self._cache[file_name]

        path = self.resolve_image(file_name)
        if not path:
            # No existe: devolver None (el consumidor puede usar un placeholder)
            self._cache[file_name] = None
            return None

        try:
            img = CoreImage(path)
            self._cache[file_name] = img
            return img
        except Exception:
            # Si falla la carga, cachear None para evitar reintentos costosos
            self._cache[file_name] = None
            return None

    def get_image_path(self, file_name):
        """
        Devuelve la ruta absoluta si existe, o None.
        """
        return self.resolve_image(file_name)

    def clear_cache(self):
        self._cache.clear()

# Exportar una instancia por conveniencia
_default_manager = ImageManager()

def resolve_image(file_name):
    return _default_manager.get_image_path(file_name)

def load_image(file_name):
    return _default_manager.load_image(file_name)

def clear_cache():
    return _default_manager.clear_cache()
