import cv2
import tensorflow as tf
import argparse
import threading
import multiprocessing
import time
import chunk_evaluator as evaluator
import slice_manager
import progressbar


def load_labels(labels_location='retrained_labels.txt'):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(labels_location).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())

    return label


def load_vidcap(file_location):
    return cv2.VideoCapture(file_location)


def get_video_fps(vidcap):
    return int(round(vidcap.get(cv2.CAP_PROP_FPS)))


def get_total_video_frames(vidcap):
    return int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

def skip_frames(vidcap, num_skip):
    frame = None
    for _ in range(0, num_skip):
        _, frame = vidcap.read()

    return frame


def process_frame(frame_image, graph_location, labels):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(graph_location, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    input_name = "import/input"
    output_name = "import/final_result"

    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
        image_reader = tf.image.decode_jpeg(frame_image, channels=3, name='jpeg_reader')
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [224, 224])
        normalized = tf.divide(tf.subtract(resized, [0]), [255])

        try:
            predictions = sess.run(normalized)
            results = sess.run(output_operation.outputs[0],
                               {input_operation.outputs[0]: predictions})
            top_k = results.argsort()[-5:][::-1]
            result_dict = {}
            for i in top_k[0]:
                result_dict[labels[i]] = results[0][i]
            return result_dict
        except Exception as e:
            print(e)


def load_and_process(frame_num, frame_to_load, all_frames):
    _, encoded_frame = cv2.imencode('.jpg', frame_to_load)
    if encoded_frame.any():
        classification = process_frame(encoded_frame.tostring(), graph_file, labels)
        all_frames[frame_num] = classification


if __name__ == "__main__":
    label_file = 'retrained_labels.txt'
    graph_file = 'retrained_graph.pb'
    video_file = ''

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help="Video to be processed")
    parser.add_argument('--graph_file', help='The graph file used to process the video file')
    parser.add_argument('--label_file', help='The label file used to process the video file')
    args = parser.parse_args()

    if args.file:
        video_file = args.file
    if args.graph_file:
        graph_file = args.graph_file
    if args.label_file:
        label_file = args.label_file

    if video_file == '':
        raise Exception("Please provide a video file to process")

    labels = load_labels(label_file)
    vidcap = load_vidcap(video_file)
    fps = get_video_fps(vidcap)
    success, frame = vidcap.read()
    frame_skip = fps / 4
    total_frames = get_total_video_frames(vidcap)

    count = 0
    frames = {}
    threads = []
    frame_types = {}

    start = time.time()
    manager = slice_manager.SliceManager()

    with progressbar.ProgressBar(max_value=total_frames) as bar:
        while success:
            bar.update(count)
            for i in range(0, multiprocessing.cpu_count()):
                process = threading.Thread(target=load_and_process, args=(count, frame, frames))
                process.start()
                threads.append(process)
                frame = skip_frames(vidcap, frame_skip)
                count += frame_skip
            
            for ii in range(len(threads)):
                threads[ii].join()
            
            evaluator.evaluate_chunk(frames, manager, count)
            frames = {}
            threads = []
        
        if manager.should_add_slice(count):
            manager.add_slice(manager.current_slice_start, count)

    print("Finished evaluating")
    print(manager.slices)
    end = time.time()
    print("Total time elapsed processing video: %f" %(end - start))
