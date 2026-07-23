#!/usr/bin/env python3
"""Build a seamless CookieBear Moments cover GIF from the project artwork."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = ROOT / "assets/images/game/adventure-world.jpg"
CHARACTER = ROOT / "assets/images/game/cookiebear-adventurer.png"
OUTPUT = ROOT / "output/imagegen/cookiebear-moments-cover.gif"

WIDTH, HEIGHT = 1080, 450
FPS, SECONDS = 8, 6
FRAME_COUNT = FPS * SECONDS
CHARACTER_HEIGHT = 342


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize and center-crop an image to fill size."""
    target_width, target_height = size
    scale = max(target_width / image.width, target_height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_width) // 2
    top = (resized.height - target_height) // 2
    return resized.crop((left, top, left + target_width, top + target_height))


def soft_circle(radius: int, color: tuple[int, int, int], alpha: int) -> Image.Image:
    size = radius * 4
    layer = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(
        (radius, radius, radius * 3, radius * 3),
        fill=(*color, alpha),
    )
    return layer.filter(ImageFilter.GaussianBlur(radius / 2))


def cloud_layer(phase: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(layer)
    clouds = (
        (180, 65, 1.0, 0.0),
        (540, 105, 0.7, 1.9),
        (900, 48, 0.52, 3.7),
    )
    for base_x, base_y, scale, offset in clouds:
        x = base_x + math.sin(phase + offset) * 42
        y = base_y + math.cos(phase + offset) * 5
        w, h = 118 * scale, 30 * scale
        fill = (255, 255, 255, 28)
        draw.ellipse((x, y, x + w, y + h), fill=fill)
        draw.ellipse((x + w * .18, y - h * .52, x + w * .57, y + h * .62), fill=fill)
        draw.ellipse((x + w * .47, y - h * .76, x + w * .86, y + h * .64), fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(3))


def particle_layer(phase: float) -> Image.Image:
    glow = Image.new("RGBA", (WIDTH, HEIGHT))
    crisp = Image.new("RGBA", (WIDTH, HEIGHT))
    glow_draw = ImageDraw.Draw(glow)
    crisp_draw = ImageDraw.Draw(crisp)
    particles = (
        (105, 342, 0.0),
        (220, 298, 1.1),
        (384, 358, 2.5),
        (557, 325, 4.2),
        (702, 375, 5.0),
        (930, 317, 3.4),
        (1010, 366, 1.8),
    )
    for base_x, base_y, offset in particles:
        wave = phase + offset
        x = base_x + math.sin(wave * 1.3) * 10
        y = base_y + math.cos(wave) * 12
        pulse = (math.sin(wave * 2) + 1) / 2
        alpha = round(70 + pulse * 170)
        radius = 2 + pulse * 1.3
        glow_draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(170, 255, 115, alpha // 2))
        crisp_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(236, 255, 167, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    glow.alpha_composite(crisp)
    return glow


def build_frames() -> list[Image.Image]:
    background = cover(Image.open(BACKGROUND).convert("RGB"), (WIDTH, HEIGHT)).convert("RGBA")
    character = Image.open(CHARACTER).convert("RGBA")
    character_width = round(character.width * CHARACTER_HEIGHT / character.height)
    character = character.resize((character_width, CHARACTER_HEIGHT), Image.Resampling.LANCZOS)
    frames: list[Image.Image] = []

    for index in range(FRAME_COUNT):
        phase = math.tau * index / FRAME_COUNT
        frame = background.copy()
        frame.alpha_composite(cloud_layer(phase))

        bob = round(math.sin(phase * 2) * 4)
        char_x = 780 + round(math.sin(phase) * 3)
        char_y = 76 + bob

        shadow = Image.new("RGBA", (WIDTH, HEIGHT))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_scale = 1 - (bob / 40)
        shadow_width = 122 * shadow_scale
        shadow_draw.ellipse(
            (char_x + 48 - shadow_width / 2, 406, char_x + 48 + shadow_width / 2, 422),
            fill=(14, 35, 25, 80),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(7))
        frame.alpha_composite(shadow)

        crystal_x = char_x + round(character_width * .79)
        crystal_y = char_y + round(CHARACTER_HEIGHT * .31)
        pulse = (math.sin(phase * 2) + 1) / 2
        glow_radius = round(15 + pulse * 8)
        glow = soft_circle(glow_radius, (71, 210, 255), round(90 + pulse * 80))
        frame.alpha_composite(
            glow,
            (crystal_x - glow.width // 2, crystal_y - glow.height // 2),
        )

        frame.alpha_composite(character, (char_x, char_y))

        sparkle = Image.new("RGBA", (WIDTH, HEIGHT))
        sparkle_draw = ImageDraw.Draw(sparkle)
        ray = round(5 + pulse * 7)
        sparkle_draw.line((crystal_x - ray, crystal_y, crystal_x + ray, crystal_y), fill=(230, 255, 255, 190), width=1)
        sparkle_draw.line((crystal_x, crystal_y - ray, crystal_x, crystal_y + ray), fill=(230, 255, 255, 190), width=1)
        frame.alpha_composite(sparkle)
        frame.alpha_composite(particle_layer(phase))
        frames.append(frame.convert("RGB"))

    return frames


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = build_frames()
    palette = frames[0].quantize(colors=192, method=Image.Quantize.MEDIANCUT)
    encoded = [
        frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
        for frame in frames
    ]
    frame_durations = [120 if index % 2 == 0 else 130 for index in range(FRAME_COUNT)]
    encoded[0].save(
        OUTPUT,
        save_all=True,
        append_images=encoded[1:],
        duration=frame_durations,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"Wrote {OUTPUT} ({FRAME_COUNT} frames, {SECONDS}s, {WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
