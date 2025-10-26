from bytetrack import BYTETracker

tracker = None
def get_tracker(model_path='models/deep_sort.pb'):
    global tracker
    if tracker is None:
        tracker = BYTETracker(track_thresh=0.5, track_buffer=30)
    return tracker

def track_objects(detections, frame):
    t = get_tracker()
    tracks = t.update_tracks(detections, frame=frame)
    return tracks
