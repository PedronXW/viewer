from deep_sort_realtime.deepsort_tracker import DeepSort

tracker = None
def get_tracker(model_path='models/deep_sort.pb'):
    global tracker
    if tracker is None:
        tracker = DeepSort(max_age=30)
    return tracker

def track_objects(detections, frame):
    t = get_tracker()
    tracks = t.update_tracks(detections, frame=frame)
    return tracks
