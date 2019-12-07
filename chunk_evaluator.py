
def get_frame_type(frame):
    if frame['snaps'] > .90:
        return 'snap'

    if frame['replays'] > .90:
        return 'replay'
    
    if frame['plays'] > .90:
        return 'play'

    if frame['other'] > .90:
        return 'other'

    return 'transition'

def evaluate_chunk(chunk):
    keys = chunk.keys()
    keys.sort()
    types = []
    for key in keys:
        frame_type = get_frame_type(chunk[key])
        print("Frame Type: %s, frame #: %d" %(frame_type, key))
        types.append(frame_type)

    if types.count(types[0]) == len(types):
        return types[0] 
    
    return 'transition'
