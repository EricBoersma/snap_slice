class SliceManager:
    slices = []
    current_slice_start = 0
    slice_skip_count = 0
    current_frame_type = ''
    play_types = ['play']
    

    def __init__(self):
        pass
    

    def add_slice(self, slice_start, slice_end):
        self.slices.append((slice_start, slice_end))
        self.slice_skip_count = 0
        self.current_slice_start = slice_end

    
    def register_slice_skip(self):
        self.slice_skip_count += 1


    def process_frame(self, frame_type, frame_count):
        if not self.current_frame_type:
            self.current_frame_type = frame_type

        if not self.current_slice_start:
            self.current_slice_start = frame_count

        if frame_type != self.current_frame_type:
            self.register_slice_skip()

        if self.slice_skip_count > 1 and frame_type in self.play_types:
            self.add_slice(self.current_slice_start, frame_count)
        