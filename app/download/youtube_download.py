from pathlib import Path

import yt_dlp

import uuid

from datetime import datetime

# =====================================
# OUTPUT ROOT
# =====================================

OUTPUT_ROOT = Path(
    "/media/ori_quadro/newhd1/Rahul/storage/outputs"
)

# =====================================
# DOWNLOAD FUNCTION
# =====================================

def download_youtube_video(url):

    unique_id = str(
        uuid.uuid4()
    )[:8]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    # =====================================
    # GET VIDEO INFO
    # =====================================

    ydl_opts_info = {

        "quiet": True
    }

    with yt_dlp.YoutubeDL(
        ydl_opts_info
    ) as ydl:

        info = ydl.extract_info(

            url,

            download=False
        )

        title = info["title"]

    safe_title = "".join(

        c for c in title

        if c.isalnum() or c in " -_"
    ).strip()

    folder_name = (
        f"{safe_title}_{timestamp}_{unique_id}"
    )

    output_folder = (
        OUTPUT_ROOT / folder_name
    )

    output_folder.mkdir(

        parents=True,

        exist_ok=True
    )

    # =====================================
    # DOWNLOAD AUDIO
    # =====================================

    output_template = str(

        output_folder / "audio.%(ext)s"
    )

    ydl_opts = {

        "format":
        "bestaudio/best",

        "outtmpl":
        output_template,

        "quiet":
        False,

        "noplaylist":
        True
    }

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        ydl.download([url])

    print("\nDOWNLOAD COMPLETED\n")

    return str(output_folder)
