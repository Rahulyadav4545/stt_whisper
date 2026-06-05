def create_semantic_chunks(

    segments,

    max_words=50,

    max_duration=8,

    max_gap= 0.5
):

    chunks = []

    current_chunk = []

    chunk_start = None

    chunk_end = None

    chunk_words = 0

    chunk_id = 0

    for segment in segments:

        text = segment["text"].strip()

        if not text:
            continue

        start = segment["start"]

        end = segment["end"]

        word_count = len(
            text.split()
        )

        # ============================
        # FIRST SEGMENT
        # ============================

        if not current_chunk:

            current_chunk.append(text)

            chunk_start = start

            chunk_end = end

            chunk_words = word_count

            continue

        gap = start - chunk_end

        projected_words = (
            chunk_words + word_count
        )

        projected_duration = (
            end - chunk_start
        )

        # ============================
        # CREATE NEW CHUNK
        # ============================

        if (

            gap > max_gap

            or

            projected_words > max_words

            or

            projected_duration > max_duration
        ):

            chunks.append({

                "chunk_id":
                chunk_id,

                "start":
                chunk_start,

                "end":
                chunk_end,

                "text":
                " ".join(current_chunk)
            })

            chunk_id += 1

            current_chunk = [text]

            chunk_start = start

            chunk_end = end

            chunk_words = word_count

        else:

            current_chunk.append(text)

            chunk_end = end

            chunk_words += word_count

    # =====================================
    # FINAL CHUNK
    # =====================================

    if current_chunk:

        chunks.append({

            "chunk_id":
            chunk_id,

            "start":
            chunk_start,

            "end":
            chunk_end,

            "text":
            " ".join(current_chunk)
        })

    return chunks