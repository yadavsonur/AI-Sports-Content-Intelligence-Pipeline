import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from configs.settings import (
    VERTICAL_WIDTH,
    VERTICAL_HEIGHT,
    HORIZONTAL_WIDTH,
    HORIZONTAL_HEIGHT,
    DEFAULT_FPS,
)


class VideoRenderer:

    def __init__(self, format_type: str = "vertical", fps: int = DEFAULT_FPS):
        self.format_type = format_type.lower().strip()
        if self.format_type == "horizontal":
            self.width = HORIZONTAL_WIDTH
            self.height = HORIZONTAL_HEIGHT
        else:
            self.width = VERTICAL_WIDTH
            self.height = VERTICAL_HEIGHT
        self.fps = fps

    def render(self, timeline, output_path: str, audio_path: str = None) -> str:
        """
        Renders an end-to-end synchronized MP4 video from a VideoTimeline and optional audio.
        Uses PIL frame composition to ensure crisp typography and 100% memory-safe rendering.
        """
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not timeline.clips:
            raise ValueError("Timeline has no clips to render")

        print(f"\n[VideoRenderer] Starting render: {len(timeline.clips)} clips | {self.width}x{self.height} @ {self.fps}fps")

        clips = []
        for index, item in enumerate(timeline.clips):
            duration = max(0.5, float(item.duration))
            frame_img = self._create_scene_frame(item.asset_url, item.caption)
            clip = ImageClip(frame_img).with_duration(duration)
            clips.append(clip)

        # Concatenate using 'chain' to avoid compositing memory overhead
        video = concatenate_videoclips(clips, method="chain")

        # Attach audio narration if provided
        audio_clip = None
        if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
            try:
                audio_clip = AudioFileClip(audio_path)
                # If audio duration exceeds video, adjust video or audio
                if audio_clip.duration > video.duration:
                    audio_clip = audio_clip.subclipped(0, video.duration)
                video = video.with_audio(audio_clip)
                print(f"[VideoRenderer] Attached narration audio ({audio_clip.duration:.2f}s)")
            except Exception as e:
                print(f"[VideoRenderer] Warning: Could not attach audio track: {e}")

        # Render video to MP4
        write_kwargs = {
            "fps": self.fps,
            "codec": "libx264",
            "ffmpeg_params": ["-preset", "veryfast", "-pix_fmt", "yuv420p"],
            "logger": None,  # Suppress verbose ffmpeg lines
        }
        if audio_clip is not None:
            write_kwargs["audio_codec"] = "aac"
        else:
            write_kwargs["audio"] = False

        try:
            video.write_videofile(output_path, **write_kwargs)
        finally:
            # Clean up open clip handles
            try:
                video.close()
                if audio_clip:
                    audio_clip.close()
                for c in clips:
                    c.close()
            except Exception:
                pass

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
            raise RuntimeError(f"Rendering failed: output file {output_path} was not created properly")

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"[VideoRenderer] Render complete: {output_path} ({file_size_mb:.2f} MB)")
        return output_path

    def _create_scene_frame(self, img_path: str, caption_text: str) -> np.ndarray:
        # Base background - deep sports dark navy
        base = Image.new("RGB", (self.width, self.height), (12, 16, 24))

        # 1. Load & Scale Image
        loaded_img = None
        if img_path and os.path.exists(img_path):
            try:
                loaded_img = Image.open(img_path).convert("RGB")
            except Exception:
                loaded_img = None

        if loaded_img is None:
            # Try repository fallback assets
            for fallback in ["assets/image1.jpg", "assets/image2.jpg", "assets/image3.jpg"]:
                if os.path.exists(fallback):
                    try:
                        loaded_img = Image.open(fallback).convert("RGB")
                        break
                    except Exception:
                        continue

        if loaded_img is not None:
            if self.format_type == "vertical":
                # In vertical mode (1080x1920), fit image nicely in middle 65% of screen
                max_w = self.width - 40
                max_h = int(self.height * 0.62)
                scale = min(max_w / loaded_img.width, max_h / loaded_img.height)
                new_w = max(10, int(loaded_img.width * scale))
                new_h = max(10, int(loaded_img.height * scale))
                resized = loaded_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Center horizontally, position in upper-middle area
                paste_x = (self.width - new_w) // 2
                paste_y = int(self.height * 0.12) + (max_h - new_h) // 2
                base.paste(resized, (paste_x, paste_y))
            else:
                # Horizontal mode (1920x1080)
                max_w = int(self.width * 0.8)
                max_h = int(self.height * 0.75)
                scale = min(max_w / loaded_img.width, max_h / loaded_img.height)
                new_w = max(10, int(loaded_img.width * scale))
                new_h = max(10, int(loaded_img.height * scale))
                resized = loaded_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                paste_x = (self.width - new_w) // 2
                paste_y = (self.height - new_h) // 2 - 40
                base.paste(resized, (paste_x, paste_y))

        # 2. Draw Readable Caption
        if caption_text and caption_text.strip():
            draw = ImageDraw.Draw(base)
            font_size = 48 if self.format_type == "vertical" else 38
            font = self._get_font(font_size)

            clean_caption = caption_text.strip().upper()
            wrapped_lines = self._wrap_text(clean_caption, draw, font, max_width=self.width - 120)

            if wrapped_lines:
                # Compute bounding box for all lines
                line_height = int(font_size * 1.3)
                total_text_h = len(wrapped_lines) * line_height
                max_line_w = max(
                    (draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0])
                    for line in wrapped_lines
                )

                pad_x = 28
                pad_y = 20
                pill_w = max_line_w + (pad_x * 2)
                pill_h = total_text_h + (pad_y * 2)

                if self.format_type == "vertical":
                    pill_y1 = int(self.height * 0.78)
                else:
                    pill_y1 = int(self.height * 0.82)

                pill_x1 = (self.width - pill_w) // 2
                pill_x2 = pill_x1 + pill_w
                pill_y2 = pill_y1 + pill_h

                # Draw high-contrast backdrop pill
                draw.rounded_rectangle(
                    [pill_x1, pill_y1, pill_x2, pill_y2],
                    radius=18,
                    fill=(0, 0, 0)
                )

                # Draw text lines
                curr_y = pill_y1 + pad_y
                for line in wrapped_lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    lw = bbox[2] - bbox[0]
                    lx = (self.width - lw) // 2
                    draw.text((lx, curr_y), line, fill=(255, 255, 255), font=font)
                    curr_y += line_height

        return np.array(base)

    def _get_font(self, size: int):
        font_candidates = ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "calibrib.ttf", "calibri.ttf"]
        for f in font_candidates:
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def _wrap_text(self, text: str, draw: ImageDraw.ImageDraw, font, max_width: int) -> list:
        words = text.split()
        if not words:
            return []

        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines
