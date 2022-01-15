# mypy: allow_any_expr
import inject

from mw_url_shortener.settings import Settings


def inject_settings(binder: inject.Binder, *, settings: Settings) -> None:
    binder.bind(Settings, settings)


def get_settings() -> Settings:
    return inject.instance(Settings)
