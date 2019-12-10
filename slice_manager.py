class SliceManager:
    slices = []
    current_slice_start = 0
    slice_skip_count = 0
    current_slice_type = ''
    play_types = ['play']
    

    def __init__(self):
        pass


    def add_slice(self, slice_start, slice_end):
        self.slices.append((slice_start, slice_end))
        self.slice_skip_count = 0
        self.current_slice_start = 0
        self.current_slice_type = ''

    
    def register_slice_skip(self):
        self.slice_skip_count += 1

    
    def should_add_slice(self, frame_count):
        return self.slice_skip_count > 1 and self.current_slice_start != frame_count and self.current_slice_type in self.play_types


    def process_frame(self, frame_type, frame_count):
        if not self.current_slice_type:
            self.current_slice_type = frame_type

        if not self.current_slice_start and frame_type in self.play_types:
            self.current_slice_start = frame_count
            self.current_slice_type = frame_type
            self.slice_skip_count = 0
        elif frame_type != self.current_slice_type and self.current_slice_start > 0:
            self.register_slice_skip()
        else:
            self.slice_skip_count = 0

        if self.should_add_slice(frame_count):
            self.add_slice(self.current_slice_start, frame_count)
        