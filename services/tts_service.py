
import os
import re
import sys
import subprocess
import wave
import array
import math

from models.narration_audio import NarrationAudio


class TTSService:
    """
    Offline local Text-to-Speech service.

    Windows: System.Speech / SAPI5
    macOS:   built-in `say` command
    Linux:   `espeak` command

    Never substitutes a tone or silence for actual speech.
    """

    def __init__(self, voice: str = None, rate: int = 0):
        self.voice = voice
        self.rate = max(-10, min(10, rate))

    def generate(self, text: str, output_path: str) -> NarrationAudio:
        if not text or not text.strip():
            raise ValueError("Cannot synthesize empty narration text.")

        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        clean_text = self._clean_text(text)

        if not output_path.lower().endswith((".wav", ".mp3")):
            output_path += ".wav"

        # Generate WAV first, including when the requested path ends in .mp3.
        wav_path = (
            output_path
            if output_path.lower().endswith(".wav")
            else output_path[:-4] + ".wav"
        )

        # Remove stale output so an old WAV cannot be mistaken for success.
        if os.path.exists(wav_path):
            os.remove(wav_path)

        if sys.platform == "win32":
            success = self._synthesize_windows_sapi(clean_text, wav_path)
        elif sys.platform == "darwin":
            success = self._synthesize_macos(clean_text, wav_path)
        else:
            success = self._synthesize_linux(clean_text, wav_path)

        if not success or not os.path.isfile(wav_path):
            raise RuntimeError(
                "Local text-to-speech failed. No valid speech WAV was produced. "
                "Check the installed speech engine and the error messages above."
            )

        self._validate_speech_wav(wav_path)

        duration = self._measure_duration(wav_path)
        if duration <= 0:
            raise RuntimeError("TTS output has an invalid duration.")

        # Keep WAV output for MoviePy and the video renderer.
        # MP3 requests currently also return the generated WAV path.
        return NarrationAudio(
            text=text,
            audio_path=wav_path,
            duration=round(duration, 2),
        )

    def _clean_text(self, text: str) -> str:
        """Remove Markdown formatting without deleting spoken punctuation."""
        text = re.sub(r"#(\w+)", r"\1", text)
        text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        text = re.sub(r"[*_`]", "", text)
        text = re.sub(r"[\[\]{}<>]", " ", text)
        text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _synthesize_windows_sapi(self, text: str, output_wav: str) -> bool:
        """
        Use PowerShell with System.Speech.

        Pass narration as Base64 UTF-8 data instead of interpolating the text
        into PowerShell source, preventing quotes or punctuation from breaking
        the script.
        """
        import base64

        text_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        path_b64 = base64.b64encode(
            output_wav.encode("utf-8")
        ).decode("ascii")

        ps_script = rf"""
$ErrorActionPreference = 'Stop'
try {{
    Add-Type -AssemblyName System.Speech

    $text = [System.Text.Encoding]::UTF8.GetString(
        [System.Convert]::FromBase64String('{text_b64}')
    )
    $path = [System.Text.Encoding]::UTF8.GetString(
        [System.Convert]::FromBase64String('{path_b64}')
    )

    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

    $voices = $synth.GetInstalledVoices() |
        Where-Object {{ $_.Enabled }}

    if (-not $voices -or $voices.Count -eq 0) {{
        throw 'No enabled Windows SAPI voices are installed.'
    }}

    if ('{self.voice or ""}' -ne '') {{
        $synth.SelectVoice('{(self.voice or "").replace("'", "''")}')
    }}

    $synth.Rate = {self.rate}
    $synth.SetOutputToWaveFile($path)
    $synth.Speak($text)
    $synth.SetOutputToNull()
    $synth.Dispose()

    if (-not (Test-Path $path)) {{
        throw 'Speech output file was not created.'
    }}

    Write-Output 'TTS_OK'
    exit 0
}}
catch {{
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}}
"""

        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    ps_script,
                ],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )

            if result.returncode != 0:
                print(f"[TTSService] Windows SAPI failed:\n{result.stderr}")
                if result.stdout.strip():
                    print(f"[TTSService] PowerShell output:\n{result.stdout}")
                return False

            return (
                os.path.isfile(output_wav)
                and os.path.getsize(output_wav) > 44
            )

        except subprocess.TimeoutExpired:
            print("[TTSService] Windows SAPI timed out after 90 seconds.")
            return False
        except Exception as exc:
            print(f"[TTSService] Windows SAPI error: {exc}")
            return False

    def _synthesize_macos(self, text: str, output_wav: str) -> bool:
        aiff_path = output_wav[:-4] + ".aiff"

        try:
            command = ["say"]
            if self.voice:
                command.extend(["-v", self.voice])

            command.extend(["-r", "175", "-o", aiff_path, text])

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )

            if result.returncode != 0:
                print(f"[TTSService] macOS say failed: {result.stderr}")
                return False

            conversion = subprocess.run(
                ["ffmpeg", "-y", "-i", aiff_path, output_wav],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if conversion.returncode != 0:
                print(f"[TTSService] WAV conversion failed: {conversion.stderr}")
                return False

            return os.path.isfile(output_wav) and os.path.getsize(output_wav) > 44

        except FileNotFoundError as exc:
            print(f"[TTSService] Required macOS command not found: {exc}")
            return False
        except Exception as exc:
            print(f"[TTSService] macOS TTS error: {exc}")
            return False
        finally:
            if os.path.exists(aiff_path):
                try:
                    os.remove(aiff_path)
                except OSError:
                    pass

    def _synthesize_linux(self, text: str, output_wav: str) -> bool:
        command = ["espeak"]

        if self.voice:
            command.extend(["-v", self.voice])

        command.extend(["-s", "160", "-w", output_wav, text])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )

            if result.returncode != 0:
                print(f"[TTSService] espeak failed: {result.stderr}")
                return False

            return os.path.isfile(output_wav) and os.path.getsize(output_wav) > 44

        except FileNotFoundError:
            print(
                "[TTSService] espeak is not installed. "
                "Install a local speech engine before generating narration."
            )
            return False
        except Exception as exc:
            print(f"[TTSService] Linux TTS error: {exc}")
            return False

    def _validate_speech_wav(self, audio_path: str) -> None:
        """Reject empty, silent, or constant-value audio."""
        with wave.open(audio_path, "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()

            if frame_count == 0 or sample_rate <= 0:
                raise RuntimeError("TTS generated an empty or invalid WAV file.")

            if sample_width != 2:
                raise RuntimeError(
                    f"Expected 16-bit PCM WAV; got {sample_width * 8}-bit audio."
                )

            raw = wav_file.readframes(frame_count)

        samples = array.array("h")
        samples.frombytes(raw)

        if sys.byteorder != "little":
            samples.byteswap()

        if not samples:
            raise RuntimeError("TTS output contains no audio samples.")

        peak = max(abs(sample) for sample in samples)
        rms = math.sqrt(
            sum(sample * sample for sample in samples) / len(samples)
        )

        if peak < 200 or rms < 50:
            raise RuntimeError(
                f"TTS output is silent or too quiet "
                f"(peak={peak}, RMS={rms:.1f})."
            )

        if max(samples) == min(samples):
            raise RuntimeError(
                "TTS output is a constant signal, not spoken narration."
            )

        print(
            f"[TTS] Validated WAV: {sample_rate} Hz, {channels} channel(s), "
            f"{frame_count / sample_rate:.2f}s, peak={peak}, RMS={rms:.1f}"
        )

    def _measure_duration(self, audio_path: str) -> float:
        if not os.path.isfile(audio_path):
            return 0.0

        try:
            with wave.open(audio_path, "rb") as wav_file:
                rate = wav_file.getframerate()
                if rate > 0:
                    return wav_file.getnframes() / float(rate)
        except (wave.Error, OSError):
            pass

        try:
            from moviepy import AudioFileClip

            with AudioFileClip(audio_path) as audio:
                return float(audio.duration or 0.0)
        except Exception as exc:
            print(f"[TTSService] Could not measure audio duration: {exc}")
            return 0.0
