
import argparse
import hashlib
import json
import shutil
import wave
import zipfile
from pathlib import Path
from datetime import datetime, timezone

PROJECT = "A VOICE FROM EARTH"
PROJECT_ID = "MO-VOICE-EARTH-2026"
CREATOR = "Mohamed Ouchane"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_wav(path):
    try:
        with wave.open(str(path), "rb") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()

            return {
                "format": "WAV PCM",
                "channels": audio.getnchannels(),
                "sample_rate_hz": rate,
                "sample_width_bits": audio.getsampwidth() * 8,
                "frames": frames,
                "duration_seconds": round(frames / rate, 3)
            }
    except (wave.Error, EOFError) as error:
        raise ValueError(
            "Unsupported audio. Please use uncompressed PCM WAV."
        ) from error


def build_package(audio_path, output_path):
    audio_path = Path(audio_path).resolve()
    output_path = Path(output_path).resolve()

    if not audio_path.is_file():
        raise FileNotFoundError("Audio file not found.")

    audio_info = inspect_wav(audio_path)

    if output_path.exists():
        raise FileExistsError(
            "Output already exists. Choose another folder."
        )

    output_path.mkdir(parents=True)

    audio_copy = output_path / "original_audio.wav"
    shutil.copy2(audio_path, audio_copy)

    checksum = sha256_file(audio_copy)

    metadata = {
        "project": PROJECT,
        "project_id": PROJECT_ID,
        "version": "1.0",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "creator": {
            "name": CREATOR,
            "origin": "Earth - Morocco"
        },

        "astronomical_context": {
            "planet": "Earth",
            "star": "Sun",
            "solar_system": "Solar System",
            "galaxy": "Milky Way",
            "galactic_region": "Orion Spur",
            "precise_coordinates": None,
            "reference_system": None,
            "note": "General context only; not a precise astronomical position."
        },

        "message": {
            "languages": [
                "Arabic",
                "Moroccan Tachelhit",
                "English"
            ],
            "audio_file": "original_audio.wav",
            "audio_metadata": audio_info,
            "target_duration_seconds": 30
        },

        "transmission": {
            "status": "NOT_TRANSMITTED",
            "destination": "Deep Space - To be determined",
            "frequency_hz": None,
            "transmission_power_w": None,
            "antenna": None,
            "modulation": None,
            "data_rate_bps": None,
            "transmitting_facility": None,
            "note": "No radio transmission has been performed."
        },

        "integrity": {
            "algorithm": "SHA-256",
            "audio_sha256": checksum
        }
    }

    metadata_file = output_path / "message.json"
    metadata_file.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    readme = f"""
{PROJECT}
{CREATOR}

This package contains the original voice recording
and its descriptive digital metadata.

Audio: original_audio.wav
Metadata: message.json

Transmission status: NOT TRANSMITTED.

This software prepares files only.
It does not generate or transmit radio signals.

Verify the original audio using SHA-256.
"""

    (output_path / "README.txt").write_text(
        readme.strip() + "\n",
        encoding="utf-8"
    )

    sums = (
        f"{checksum}  original_audio.wav\n"
        f"{sha256_file(metadata_file)}  message.json\n"
    )

    (output_path / "SHA256SUMS.txt").write_text(
        sums,
        encoding="utf-8"
    )

    zip_path = output_path.parent / (
        output_path.name + ".zip"
    )

    with zipfile.ZipFile(
        zip_path, "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for item in output_path.iterdir():
            archive.write(item, arcname=item.name)

    print("\nPackage created successfully.")
    print("Folder:", output_path)
    print("ZIP:", zip_path)
    print("Audio duration:", audio_info["duration_seconds"], "seconds")
    print("SHA-256:", checksum)
    print("\nTransmission status: NOT TRANSMITTED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A Voice from Earth Encoder"
    )

    parser.add_argument(
        "--audio",
        required=True,
        help="Path to your original WAV audio"
    )

    parser.add_argument(
        "--output",
        default="A_VOICE_FROM_EARTH",
        help="Output folder name"
    )

    args = parser.parse_args()

    try:
        build_package(args.audio, args.output)
    except Exception as error:
        print("ERROR:", error)
