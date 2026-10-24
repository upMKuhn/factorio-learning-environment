"""Sprite download/extraction pipeline lives with the render tool that consumes it."""

from fle.env.tools.admin.render.sprites.download import (
    download_sprites_from_hf,
    generate_sprites,
)


def test_entry_points_are_callable():
    assert callable(download_sprites_from_hf)
    assert callable(generate_sprites)


def test_generate_sprites_reports_missing_input(tmp_path):
    assert generate_sprites(str(tmp_path / "missing"), str(tmp_path / "out")) is False


def test_extractors_import():
    from fle.env.tools.admin.render.sprites.extractors.alerts import AlertSpriteExtractor
    from fle.env.tools.admin.render.sprites.extractors.entities import (
        EntitySpritesheetExtractor,
    )
    from fle.env.tools.admin.render.sprites.extractors.icons import IconSpriteExtractor

    assert AlertSpriteExtractor and EntitySpritesheetExtractor and IconSpriteExtractor
