
def get_frame_type(frame):
    if frame['snaps'] > .90:
        return 'play'

    if frame['replays'] > .90:
        return 'replay'
    
    if frame['plays'] > .90:
        return 'play'

    if frame['other'] > .90:
        return 'other'

    return 'transition'


def evaluate_chunk(chunk, slice_evaluator, frame_count):
    keys = chunk.keys()
    keys.sort()
    for key in keys:
        frame_type = get_frame_type(chunk[key])
        slice_evaluator.process_frame(frame_type, frame_count)

