from fastapi import HTTPException, UploadFile


ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/aac",
    "audio/ogg",
    "video/webm",
    "application/octet-stream",
}

MAX_AUDIO_UPLOAD_BYTES = 15 * 1024 * 1024


async def validate_audio_upload(audio_file: UploadFile):
    if audio_file is None:
        raise HTTPException(status_code=400, detail="audio_file is required")

    content_type = audio_file.content_type or "application/octet-stream"

    if content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported audio file type",
                "content_type": content_type,
                "allowed_types": sorted(ALLOWED_AUDIO_CONTENT_TYPES),
            },
        )

    audio_file.file.seek(0, 2)
    size = audio_file.file.tell()
    audio_file.file.seek(0)

    if size <= 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    if size > MAX_AUDIO_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large. Max allowed is {MAX_AUDIO_UPLOAD_BYTES} bytes.",
        )

    return {
        "content_type": content_type,
        "size_bytes": size,
    }
