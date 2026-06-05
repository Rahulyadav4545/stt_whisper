import sys

sys.path.append(
    "/media/ori_quadro/newhd1/Rahul"
)

from pathlib import Path

from backend.app.chunking.run_chunking import (
    run_chunking
)

from backend.app.vectordb.run_vectordb import (
    run_vectordb
)

from backend.app.services.summary_service import (
    generate_video_summary
)

# =========================================
# OUTPUTS FOLDER
# =========================================

OUTPUTS_FOLDER = Path(
    "/media/ori_quadro/newhd1/Rahul/storage/outputs"
)

# =========================================
# PROCESS ALL VIDEOS
# =========================================

def run_pipeline():

    folders = [

        folder

        for folder in OUTPUTS_FOLDER.iterdir()

        if folder.is_dir()
    ]

    if len(folders) == 0:

        print("\nNO OUTPUT FOLDERS FOUND\n")

        return

    print(
        f"\nFOUND {len(folders)} VIDEO FOLDERS\n"
    )

    for folder in sorted(folders):

        print("\n=================================")
        print(f"PROCESSING: {folder.name}")
        print("=================================\n")

        # =====================================
        # CHECK TRANSCRIPT
        # =====================================

        transcript_path = (
            folder / "transcript.json"
        )

        if not transcript_path.exists():

            print(
                f"\nSKIPPING: {folder.name}"
            )

            print(
                "transcript.json NOT FOUND\n"
            )

            continue

        try:

            # =====================================
            # STEP 1 : CHUNKING
            # =====================================

            print("\nSTEP 1 : CHUNKING\n")

            run_chunking(
                str(folder)
            )

            # =====================================
            # STEP 2 : VECTOR DB
            # =====================================

            print("\nSTEP 2 : VECTOR DB\n")

            run_vectordb(
                str(folder)
            )

            # =====================================
            # STEP 3 : SUMMARY
            # =====================================

            print("\nSTEP 3 : SUMMARY\n")

            generate_video_summary(
                str(folder)
            )

            print(
                f"\nCOMPLETED: {folder.name}\n"
            )

        except Exception as e:

            print(
                f"\nFAILED: {folder.name}"
            )

            print(str(e))

    print("\nALL VIDEOS PROCESSED\n")


# =========================================
# ENTRY
# =========================================

if __name__ == "__main__":

    run_pipeline()