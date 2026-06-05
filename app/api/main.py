# #=#
# # INSTALL FIRST
# #
# # sudo apt update
# # sudo apt install ffmpeg -y
# #
# # pip install faster-whisper
# # pip install torch torchaudio
# # pip install ffmpeg-python
# # pip install yt-dlp
# # pip install requests
# #

# import os
# import re
# import json
# import uuid
# import logging
# import warnings

# from pathlib import Path
# from datetime import datetime
# from urllib.parse import urlparse
# BASE_DIR = Path("/media/ori_quadro/newhd1/Rahul")

# DOWNLOADS_DIR = BASE_DIR / "storage" / "uploads"
# OUTPUTS_DIR = BASE_DIR / "storage" / "outputs"
# import torch
# import ffmpeg
# import yt_dlp
# import requests

# from faster_whisper import WhisperModel

# # WARNINGS

# warnings.filterwarnings("ignore")
# # LOGGING

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
# )

# logger = logging.getLogger(__name__)

# # CONFIG

# CONFIG = {

#     #=========
#     # OUTPUT FOLDERS
#     #=========

#     "downloads_dir":
# str(DOWNLOADS_DIR),

# "output_dir":
# str(OUTPUTS_DIR),

#     #=========
#     # WHISPER MODEL
#     #=========

#     "model_size":
#     "large-v3",

#     #=========
#     # TRANSCRIPTION SETTINGS
#     #=========

#     "beam_size":
#     5,

#     "best_of":
#     5,

#     "temperature":
#     0.0,

#     "vad_filter":
#     True,

#     "word_timestamps":
#     True,

#     "condition_on_previous_text":
#     True,

#     "compression_ratio_threshold":
#     2.4,

#     "log_prob_threshold":
#     -1.0,

#     "no_speech_threshold":
#     0.6,

#     #=========
#     # CLEANING FILTERS
#     #=========

#     "min_segment_duration":
#     0.0,

#     "min_words":
#     0,

#     "min_avg_logprob":
#     -999.0
# }

# # CREATE DIRS

# os.makedirs(
#     CONFIG["downloads_dir"],
#     exist_ok=True
# )

# os.makedirs(
#     CONFIG["output_dir"],
#     exist_ok=True
# )

# # DEVICE

# DEVICE = (
#     "cuda"
#     if torch.cuda.is_available()
#     else "cpu"
# )

# COMPUTE_TYPE = (
#     "float16"
#     if DEVICE == "cuda"
#     else "int8"
# )

# logger.info(f"Using device: {DEVICE}")

# # SUPPORTED FORMATS

# SUPPORTED_FORMATS = [

#     ".mp3",
#     ".wav",
#     ".m4a",
#     ".mp4",
#     ".aac",
#     ".ogg",
#     ".flac",
#     ".mov",
#     ".mkv"
# ]
# # URL CHECK

# def is_url(path: str):

#     return path.startswith(
#         ("http://", "https://")
#     )

# # YOUTUBE CHECK
# from urllib.parse import parse_qs

# def extract_youtube_id(url: str):

#     parsed = urlparse(url)

#     if parsed.hostname in ["www.youtube.com", "youtube.com"]:
#         return parse_qs(parsed.query).get("v", [None])[0]

#     if parsed.hostname == "youtu.be":
#         return parsed.path[1:]

#     return None
# def is_youtube_url(url: str):

#     youtube_domains = [

#         "youtube.com",
#         "youtu.be"
#     ]

#     parsed = urlparse(url)

#     return any(
#         domain in parsed.netloc
#         for domain in youtube_domains
#     )

# # VALIDATE FILE

# def validate_local_file(
#     file_path: str
# ):

#     if not os.path.exists(file_path):

#         raise FileNotFoundError(
#             f"File not found: {file_path}"
#         )

#     ext = Path(file_path).suffix.lower()

#     if ext not in SUPPORTED_FORMATS:

#         raise ValueError(
#             f"Unsupported format: {ext}"
#         )

# # DOWNLOAD YOUTUBE

# def download_youtube_audio(
#     url: str
# ):

#     logger.info(
#         "Downloading YouTube audio..."
#     )

#     youtube_id = extract_youtube_id(url)

#     print("YouTube ID:", youtube_id)

#     ydl_opts = {

#         "format":
#         "bestaudio/best",

#         "outtmpl":
#         f"{CONFIG['downloads_dir']}/%(title)s.%(ext)s",

#         "quiet":
#         True,

#         "noplaylist":
#         True
#     }

#     try:

#         with yt_dlp.YoutubeDL(
#             ydl_opts
#         ) as ydl:

#             info = ydl.extract_info(
#                 url,
#                 download=True
#             )

#             downloaded_file = (
#                 ydl.prepare_filename(
#                     info
#                 )
#             )

#         logger.info(
#             "YouTube download completed."
#         )

#         return downloaded_file

#     except Exception as e:

#         logger.error(str(e))

#         raise RuntimeError(
#             "YouTube download failed."
#         )
# # DOWNLOAD DIRECT URL

# def download_direct_file(
#     url: str
# ):

#     logger.info(
#         "Downloading file..."
#     )

#     filename = os.path.join(

#         CONFIG["downloads_dir"],

#         os.path.basename(
#             urlparse(url).path
#         )
#     )

#     try:

#         response = requests.get(
#             url,
#             stream=True
#         )

#         response.raise_for_status()

#         with open(
#             filename,
#             "wb"
#         ) as f:

#             for chunk in response.iter_content(
#                 chunk_size=8192
#             ):

#                 if chunk:
#                     f.write(chunk)

#         logger.info(
#             "Direct download completed."
#         )

#         return filename

#     except Exception as e:

#         logger.error(str(e))

#         raise RuntimeError(
#             "Direct file download failed."
#         )

# # PROCESS INPUT

# def process_input(
#     input_source: str
# ):

#     if not is_url(
#         input_source
#     ):

#         validate_local_file(
#             input_source
#         )

#         return input_source

#     if is_youtube_url(
#         input_source
#     ):

#         return download_youtube_audio(
#             input_source
#         )

#     return download_direct_file(
#         input_source
#     )
# # CREATE UNIQUE OUTPUT PATHS

# def create_output_paths(input_file):

#     base_name = Path(input_file).stem
#         # CHECK DUPLICATE VIDEO

#     existing_folders = os.listdir(
#         CONFIG["output_dir"]
#     )

#     for folder in existing_folders:

#         if folder.startswith(base_name):

#             print("\nTHIS DATA IS ALREADY STORED\n")

#             return None

#     unique_id = str(uuid.uuid4())[:8]

#     timestamp = datetime.now().strftime(
#         "%Y%m%d_%H%M%S"
#     )

#     folder_name = (
#         f"{base_name}_{timestamp}_{unique_id}"
#     )

#     output_folder = os.path.join(
#         CONFIG["output_dir"],
#         folder_name
#     )

#     os.makedirs(
#         output_folder,
#         exist_ok=True
#     )

#     return {

#         "output_folder":
#         output_folder,

#         "clean_audio":
#         os.path.join(
#             output_folder,
#             "clean_audio.wav"
#         ),

#         "transcript_json":
#         os.path.join(
#             output_folder,
#             "transcript.json"
#         ),

#         "transcript_txt":
#         os.path.join(
#             output_folder,
#             "transcript.txt"
#         )
#     }
# # AUDIO CONVERSION

# def convert_audio(
#     input_path: str,
#     output_path: str
# ):

#     logger.info(
#         "Converting audio to "
#         "16kHz mono WAV..."
#     )

#     try:

#         (
#             ffmpeg
#             .input(input_path)
#             .output(
#                 output_path,
#                 ac=1,
#                 ar=16000,
#                 format="wav"
#             )
#             .overwrite_output()
#             .run(
#                 quiet=True
#             )
#         )

#         logger.info(
#             "Audio conversion completed."
#         )

#     except ffmpeg.Error as e:

#         logger.error(str(e))

#         raise RuntimeError(
#             "Audio conversion failed."
#         )
# # LOAD WHISPER MODEL

# def load_model():

#     logger.info(
#         f"Loading model: "
#         f"{CONFIG['model_size']}"
#     )

#     try:

#         model = WhisperModel(

#             CONFIG["model_size"],

#             device=DEVICE,

#             compute_type=COMPUTE_TYPE
#         )

#         logger.info(
#             "Model loaded successfully."
#         )

#         return model

#     except Exception as e:

#         logger.error(str(e))

#         raise RuntimeError(
#             "Whisper model loading failed."
#         )
# # CLEAN TEXT

# def clean_text(
#     text: str
# ):

#     text = re.sub(
#         r"\s+",
#         " ",
#         text
#     )

#     text = re.sub(
#         r"\b(\w+)( \1\b)+",
#         r"\1",
#         text,
#         flags=re.IGNORECASE
#     )

#     return text.strip()

# # TRANSCRIBE AUDIO

# def transcribe_audio(
#     model,
#     audio_path: str
# ):

#     logger.info(
#         "Starting transcription..."
#     )

#     try:

#         segments, info = model.transcribe(

#             audio_path,

#             beam_size=CONFIG[
#                 "beam_size"
#             ],

#             best_of=CONFIG[
#                 "best_of"
#             ],

#             temperature=CONFIG[
#                 "temperature"
#             ],

#             vad_filter=CONFIG[
#                 "vad_filter"
#             ],

#             word_timestamps=CONFIG[
#                 "word_timestamps"
#             ],

#             multilingual=True,

#             condition_on_previous_text=CONFIG[
#                 "condition_on_previous_text"
#             ],

#             compression_ratio_threshold=CONFIG[
#                 "compression_ratio_threshold"
#             ],

#             log_prob_threshold=CONFIG[
#                 "log_prob_threshold"
#             ],

#             no_speech_threshold=CONFIG[
#                 "no_speech_threshold"
#             ]
#         )

#         logger.info(
#             f"Detected language: "
#             f"{info.language}"
#         )

#         transcript_segments = []

#         transcript_text = []

#         segment_counter = 0

#         for segment in segments:

#             start = round(
#                 segment.start,
#                 2
#             )

#             end = round(
#                 segment.end,
#                 2
#             )

#             duration = end - start

#             text = clean_text(
#                 segment.text
#             )

#             words = []

#             if segment.words:

#                 for word in segment.words:

#                     word_text = clean_text(
#                         word.word
#                     )

#                     if not word_text:
#                         continue

#                     words.append({

#                         "word":
#                         word_text,

#                         "start":
#                         round(
#                             word.start,
#                             2
#                         ),

#                         "end":
#                         round(
#                             word.end,
#                             2
#                         ),

#                         "probability":
#                         round(
#                             word.probability,
#                             4
#                         )
#                     })

#             segment_data = {

#                 "segment_id":
#                 segment_counter,

#                 "start":
#                 start,

#                 "end":
#                 end,

#                 "duration":
#                 round(duration, 2),

#                 "text":
#                 text,

#                 "speaker":
#                 None,

#                 "avg_logprob":
#                 round(
#                     float(
#                         segment.avg_logprob
#                     ),
#                     4
#                 ),

#                 "no_speech_prob":
#                 round(
#                     float(
#                         segment.no_speech_prob
#                     ),
#                     4
#                 ),

#                 "word_count":
#                 len(
#                     text.split()
#                 ),

#                 "words":
#                 words
#             }

#             transcript_segments.append(
#                 segment_data
#             )

#             chunk = (
#                 f"[{start}s --> {end}s]\n"
#                 f"{text}\n"
#             )

#             print(chunk)

#             transcript_text.append(
#                 chunk
#             )

#             segment_counter += 1

#         final_output = {

#             "source_file":
#             audio_path,

#             "language":
#             info.language,

#             "language_probability":
#             round(
#                 float(
#                     info.language_probability
#                 ),
#                 4
#             ),

#             "device":
#             DEVICE,

#             "model":
#             CONFIG["model_size"],

#             "total_segments":
#             len(
#                 transcript_segments
#             ),

#             "segments":
#             transcript_segments
#         }

#         return (
#             final_output,
#             transcript_text
#         )

#     except Exception as e:

#         logger.error(str(e))

#         raise RuntimeError(
#             "Transcription failed."
#         )
# # SAVE JSON

# def save_json(
#     data,
#     path: str
# ):

#     logger.info(
#         f"Saving JSON: {path}"
#     )

#     with open(
#         path,
#         "w",
#         encoding="utf-8"
#     ) as f:

#         json.dump(
#             data,
#             f,
#             indent=4,
#             ensure_ascii=False
#         )
# # SAVE TXT

# def save_txt(
#     chunks,
#     path: str
# ):

#     logger.info(
#         f"Saving TXT: {path}"
#     )

#     with open(
#         path,
#         "w",
#         encoding="utf-8"
#     ) as f:

#         f.write(
#             "\n".join(chunks)
#         )
# # MAIN

# def main():

#     try:

#         #=========
#         # INPUT PATH
#         #=========

#         input_source = input(
#             "\nEnter file path, folder path, or URL:\n\n"
#         ).strip()

#         #=========
#         # LOAD MODEL ONCE
#         #=========

#         model = load_model()

#         #=========
#         # FILE LIST
#         #=========

#         files_to_process = []

#         #=========
#         # URL INPUT
#         #=========

#         if is_url(input_source):

#             files_to_process.append(
#                 input_source
#             )

#         #=========
#         # FOLDER INPUT
#         #=========

#         elif os.path.isdir(input_source):

#             for file_name in os.listdir(
#                 input_source
#             ):

#                 full_path = os.path.join(
#                     input_source,
#                     file_name
#                 )

#                 ext = Path(
#                     full_path
#                 ).suffix.lower()

#                 if ext in SUPPORTED_FORMATS:

#                     files_to_process.append(
#                         full_path
#                     )

#         #=========
#         # SINGLE FILE INPUT
#         #=========

#         else:

#             validate_local_file(
#                 input_source
#             )

#             files_to_process.append(
#                 input_source
#             )

#         #=========
#         # NO FILES
#         #=========

#         if not files_to_process:

#             raise ValueError(
#                 "No supported audio/video files found."
#             )

#         #=========
#         # PROCESS ALL FILES
#         #=========

#         for index, input_item in enumerate(
#             files_to_process,
#             start=1
#         ):

#             try:

#                 logger.info(
#                     f"\nPROCESSING FILE "
#                     f"{index}/{len(files_to_process)}"
#                 )

                
#                 # PROCESS INPUT
                

#                 real_input_file = process_input(
#                     input_item
#                 )

#                 logger.info(
#                     f"Input ready: "
#                     f"{real_input_file}"
#                 )

                
#                 # CREATE OUTPUT PATHS
                

#                 paths = create_output_paths(
#                     real_input_file
#                 )
#                 if paths is None:
#                     continue

                
#                 # CONVERT AUDIO
                

#                 convert_audio(

#                     real_input_file,

#                     paths["clean_audio"]
#                 )

                
#                 # TRANSCRIBE
                

#                 transcript_json, transcript_txt = (
#                     transcribe_audio(

#                         model,

#                         paths["clean_audio"]
#                     )
#                 )

                
#                 # SAVE JSON
                

#                 save_json(

#                     transcript_json,

#                     paths["transcript_json"]
#                 )

                
#                 # SAVE TXT
                

#                 save_txt(

#                     transcript_txt,

#                     paths["transcript_txt"]
#                 )

#                 logger.info(
#                     "FILE COMPLETED SUCCESSFULLY"
#                 )

#                 print("\nOUTPUT FOLDER:\n")
#                 print(paths["output_folder"])

#             except Exception as file_error:

#                 logger.error(
#                     f"FAILED FILE: "
#                     f"{input_item}"
#                 )

#                 logger.error(
#                     str(file_error)
#                 )

#         logger.info(
#             "\nALL PROCESSING COMPLETED"
#         )

#     except Exception as e:

#         logger.error(str(e))

# # ENTRY
# if __name__ == "__main__":
#     main()

