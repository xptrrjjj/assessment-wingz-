import importlib
import pkgutil

from django.urls import include, path

from core.api.router import router
import modules

discovered_urlpatterns = []
for _importer, module_name, _is_pkg in pkgutil.iter_modules(modules.__path__):
    try:
        mod = importlib.import_module(f"modules.{module_name}.api.v1.urls")
        if hasattr(mod, "urlpatterns"):
            discovered_urlpatterns.append(
                path(f"v1/{module_name}/", include(mod))
            )
    except ModuleNotFoundError:
        pass

urlpatterns = [
    path("v1/", include(router.urls)),
    *discovered_urlpatterns,
]
