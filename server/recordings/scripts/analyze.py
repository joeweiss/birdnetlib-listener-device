# This example requires arecord, which is available on most Linux systems.
# Record to 15 second files with arecord, then analyze with two analyzers.

from datetime import datetime
from pprint import pprint
import os

from django.conf import settings

from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.batch import DirectoryAnalyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
from birdnetlib.analyzer import Analyzer
from recordings.utils import import_from_recording
import shutil

from django.db.utils import OperationalError

RECORDING_DIR = settings.INGEST_WAV_FILE_DIRECTORY
OUTPUT_DIR = settings.OUTPUT_WAV_FILE_DIRECTORY
ARCHIVE_AUDIO_FILES = False
DELETE_IF_NO_DETECTIONS = True
PROCESS_EXISTING_BEFORE_WATCHING = True

DETECTION_CONFIDENCE_THRESHOLD = settings.DETECTION_CONFIDENCE_THRESHOLD

print("DETECTION_CONFIDENCE_THRESHOLD", DETECTION_CONFIDENCE_THRESHOLD)
print("RECORDING_DIR", RECORDING_DIR)
print("OUTPUT_DIR", OUTPUT_DIR)

def on_analyze_complete(recording):
    print("on_analyze_complete")
    # Each analyzation as it is completed.
    print(recording.path, recording.analyzer.name)
    pprint(recording.detections)


def on_analyze_file_complete(recording_list):
    print("---------------------------")
    print("on_analyze_file_complete")
    print("---------------------------")
    # All analyzations are completed. Results passed as a list of Recording objects.

    if len(recording_list) == 0:
        return

    num_detections = 0
    for recording in recording_list:

        # Only import recordings with detections.
        if len(recording.detections) == 0:
            continue
        rec_obj = None
        try:
            rec_obj = import_from_recording(recording)
        except OperationalError:
            print("Error establishing a database connection")
            pass

        pprint(recording.detections)
        num_detections = num_detections + len(recording.detections)
        print("---------------------------")
    if ARCHIVE_AUDIO_FILES == False:
        print("Deleting", recording.path)
        os.remove(recording.path)
        return
    if num_detections == 0 and DELETE_IF_NO_DETECTIONS:
        print("Deleting", recording.path)
        os.remove(recording.path)
    else:
        if rec_obj:
            rec_obj.archive_file()
        else:
            new_path = os.path.join(OUTPUT_DIR, os.path.basename(recording.filename))
            shutil.move(
                recording.path,
                new_path,
            )


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


def preanalyze(recording):
    # Used to modify the recording object before analyzing.
    filename = recording.filename
    # 2022-08-15-birdnet-21:05:51.wav, as an example, use BirdNET-Pi's preferred format for testing.
    dt = datetime.strptime(filename, "%Y-%m-%d-%H:%M:%S.wav")
    # Modify the recording object here as needed.
    # For testing, we're changing the date. We could also modify lat/long here.
    recording.date = dt


def main():

    recording_dir = RECORDING_DIR

    print("Starting Analyzers")

    directory = recording_dir

    # Use both analyzers.
    # analyzer_lite = LiteAnalyzer()
    # analyzer = Analyzer()
    # analyzers = [analyzer, analyzer_lite]

    # Use a single analyzer.
    analyzer = Analyzer()
    analyzers = [analyzer]

    lon = settings.LONGITUDE
    lat = settings.LATITUDE
    min_conf = DETECTION_CONFIDENCE_THRESHOLD

    print("LATITUDE", lat)
    print("LONGITUDE", lon)

    if PROCESS_EXISTING_BEFORE_WATCHING:
        print("Processing existing")
        directory_analyzer = DirectoryAnalyzer(
            directory,
            analyzers=analyzers,
            lon=lon,
            lat=lat,
            min_conf=min_conf,
        )
        directory_analyzer.recording_preanalyze = preanalyze
        directory_analyzer.on_analyze_complete = on_analyze_complete
        directory_analyzer.on_analyze_file_complete = on_analyze_file_complete
        directory_analyzer.on_error = on_error
        directory_analyzer.process()

    print("Starting Watcher")

    watcher = DirectoryWatcher(
        directory,
        analyzers=analyzers,
        lon=lon,
        lat=lat,
        min_conf=min_conf,
        use_polling=True,
    )
    watcher.recording_preanalyze = preanalyze
    watcher.on_analyze_complete = on_analyze_complete
    watcher.on_analyze_file_complete = on_analyze_file_complete
    watcher.on_error = on_error
    watcher.watch()


def run():
    print("watch_and_analyze")
    main()
