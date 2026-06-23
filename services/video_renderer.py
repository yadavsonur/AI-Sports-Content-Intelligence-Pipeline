from moviepy import (
    ImageClip,
    TextClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips
)


class VideoRenderer:

    WIDTH = 1280
    HEIGHT = 720

    def render(
        self,
        timeline,
        output_path
    ):

        clips = []

        print(
            "\n========== RENDER START ==========\n"
        )

        for index, item in enumerate(
            timeline.clips
        ):

            print(
                f"\n----- Scene {index} -----"
            )

            print(
                f"Image: {item.asset_url}"
            )

            image_clip = (
                ImageClip(
                    item.asset_url
                )
                .resized(
                    height=self.HEIGHT
                )
                .with_duration(
                    item.duration
                )
            )

            print(
                f"Image Size: "
                f"{image_clip.size}"
            )

            background = (
                ColorClip(
                    size=(
                        self.WIDTH,
                        self.HEIGHT
                    ),
                    color=(
                        0,
                        0,
                        0
                    )
                )
                .with_duration(
                    item.duration
                )
            )

            caption = (
                TextClip(
                    text=item.caption,
                    font_size=60,
                    color="white"
                )
                .with_duration(
                    item.duration
                )
                .with_position(
                    (
                        "center",
                        self.HEIGHT - 120
                    )
                )
            )

            final_clip = (
                CompositeVideoClip(
                    [
                        background,
                        image_clip.with_position(
                            "center"
                        ),
                        caption
                    ],
                    size=(
                        self.WIDTH,
                        self.HEIGHT
                    )
                )
                .with_duration(
                    item.duration
                )
            )

            print(
                f"Final Clip Size: "
                f"{final_clip.size}"
            )

            clips.append(
                final_clip
            )

        print(
            "\nConcatenating clips..."
        )

        video = (
            concatenate_videoclips(
                clips,
                method="compose"
            )
        )

        print(
            f"Video Size: "
            f"{video.size}"
        )

        print(
            "\nWriting file..."
        )

        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio=False
        )

        print(
            "\n========== DONE ==========\n"
        )

        return output_path