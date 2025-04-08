import os
from pydub import AudioSegment

def batch_convert(input_folder, output_folder):
    # Path to the folder containing .m4a files
    input_folder = "path/to/your/folder"
    output_folder = os.path.join(input_folder, "converted_mp3")

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".m4a"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".mp3"
            output_path = os.path.join(output_folder, output_filename)

            # Convert and export as mp3
            audio = AudioSegment.from_file(input_path, format="m4a")
            audio.export(output_path, format="mp3")
            print(f"Converted: {filename} → {output_filename}")

    print("✅ Batch conversion completed.")