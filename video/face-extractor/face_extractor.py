import logging
import os
import pickle
import shutil
import time
from collections import defaultdict
from typing import List
import tempfile
from io import BytesIO

import cv2
import face_recognition
import numpy as np
from imutils import paths
from indexify_extractor_sdk import Content, Extractor, Feature
from PIL import Image
from sklearn.cluster import DBSCAN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceExtractor(Extractor):
    name = "tensorlake/face-extractor"
    description = "Extract unique faces from a video"
    python_dependencies = [
        "scikit-learn",
        "pillow",
        "numpy",
        "face_recognition",
        "opencv-python",
        "imutils",
    ]
    system_dependencies = []
    input_mime_types = ["video", "video/mp4"]

    def extract(self, content: Content, params: None) -> List[Content]:
        content.content_type
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            tmpfile_name = tmpfile.name
            tmpfile.write(content.data)
            tmpfile.flush()

        # Now use OpenCV to read the video
        self.filename = tmpfile_name

        if not os.path.exists(self.filename):
            raise ValueError(f"file: {self.filename} not found")

        self.save_fps = 1
        self.frame_freq = 60

        data_dir = "data"
        self.encodings_pkl_path = os.path.join(data_dir, "encodings.pickle")

        self.frames_dir = os.path.join(data_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)

        self.encodings_dir = os.path.join(data_dir, "encodings")
        os.makedirs(self.encodings_dir, exist_ok=True)

        # process data
        self.extract_frames()
        self.extract_encodings()
        cluster_images = self.cluster_images()

        # clean up
        os.remove(tmpfile_name)
        shutil.rmtree("data")
        content_list = []
        for k in cluster_images.keys():
            feature = Feature.metadata(
                {"face": str(k), "frame": cluster_images[k][0]["frame"]}, name="image"
            )
            img = Image.fromarray(cluster_images[k][0]["image"])

            output = BytesIO()
            img = img.convert("RGB")
            img.save(output, format="JPEG")

            content_list.append(
                Content(
                    content_type=f"image/jpeg",
                    data=output.getvalue(),
                    features=[feature],
                )
            )

        return content_list

    def __init__(self, frame_freq=60, save_fps=1):
        super(FaceExtractor, self).__init__()

    def _rescale_by_height(self, image, target_height, method=cv2.INTER_LANCZOS4):
        """Rescale `image` to `target_height` (preserving aspect ratio)."""
        w = int(round(target_height * image.shape[1] / image.shape[0]))
        return cv2.resize(image, (w, target_height), interpolation=method)

    # Given a target width, adjust the image by calculating the height and resize
    def _rescale_by_width(self, image, target_width, method=cv2.INTER_LANCZOS4):
        """Rescale `image` to `target_width` (preserving aspect ratio)."""
        h = int(round(target_width * image.shape[0] / image.shape[1]))
        return cv2.resize(image, (target_width, h), interpolation=method)

    def _auto_resize(self, frame):
        height, width, _ = frame.shape

        if height > 500:
            frame = self._rescale_by_height(frame, 500)
            self._auto_resize(frame)

        if width > 700:
            frame = self._rescale_by_width(frame, 700)
            self._auto_resize(frame)

        return frame

    def extract_frames(self):
        cap = cv2.VideoCapture(self.filename)
        _, frame = cap.read()

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        logger.info(f"Total Frames {total_frames} @ {fps} fps")
        logger.info("Calculating number of frames per second")

        if os.path.exists(self.frames_dir):
            shutil.rmtree(self.frames_dir)
            time.sleep(0.5)
        os.mkdir(self.frames_dir)

        frame_count = 1
        while frame_count < total_frames:
            success, frame = cap.read()
            if not success:
                break
            if frame_count % int(fps * self.save_fps) == 0:
                logger.info(f"Saving frame number {frame_count}")
                frame = self._auto_resize(frame)
                filename = str(frame_count) + ".jpg"
                cv2.imwrite(os.path.join(self.frames_dir, filename), frame)
            frame_count += 1
        logger.info("Frames extracted")

    def extract_encodings(self):
        logger.info("Extract Encodings")
        data = []
        for id, image_path in enumerate(paths.list_images(self.frames_dir)):
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="cnn")
            encodings = face_recognition.face_encodings(rgb, boxes)
            d = [
                {"image_path": image_path, "loc": box, "encoding": enc}
                for (box, enc) in zip(boxes, encodings)
            ]
            data.append({"id": id, "encodings": d})
            logger.info(f"Extract {id}")
        self.encodings_to_pkl(data)
        self.generate_main_encodings_pkl()
        logger.info("DONE")

    def encodings_to_pkl(self, data):
        for d in data:
            encodings = d["encodings"]
            id = d["id"]
            with open(
                os.path.join(self.encodings_dir, "encodings_" + str(id) + ".pickle"),
                "wb",
            ) as f:
                f.write(pickle.dumps(encodings))

    def generate_main_encodings_pkl(self):
        datastore = []
        pickle_paths = []

        for path in os.listdir(self.encodings_dir):
            if path.endswith(".pickle"):
                pickle_paths.append(os.path.join(self.encodings_dir, path))

        for pickle_path in pickle_paths:
            with open(pickle_path, "rb") as f:
                data = pickle.loads(f.read())
                datastore.extend(data)

        with open(self.encodings_pkl_path, "wb") as f:
            f.write(pickle.dumps(datastore))

    def crop_image(self, loc, image):
        (o_top, o_right, o_bottom, o_left) = loc
        height, width, channel = image.shape

        widthMargin = 10
        heightMargin = 20

        top = o_top - heightMargin
        if top < 0:
            top = 0

        bottom = o_bottom + heightMargin
        if bottom > height:
            bottom = height

        left = o_left - widthMargin
        if left < 0:
            left = 0

        right = o_right + widthMargin
        if right > width:
            right = width

        image = image[top:bottom, left:right]
        image = self._rescale_by_width(image, 100)
        return image

    def cluster_images(self, max_per_label=1):
        # load the serialized face encodings + bounding box locations from
        # disk, then extract the set of encodings to so we can cluster on
        # them
        logger.info("Loading encodings")
        encodings_data = pickle.loads(open(self.encodings_pkl_path, "rb").read())
        encodings_data = np.array(encodings_data)

        encodings = [d["encoding"] for d in encodings_data]

        # cluster the embeddings
        logger.info("Clustering")
        clt = DBSCAN(eps=0.5, metric="euclidean", n_jobs=1)
        clt.fit(encodings)
        logger.info("DONE")

        # determine the total number of unique faces found in the dataset
        labels = clt.labels_
        label_ids = np.unique(labels)
        unique_faces_count = len(np.where(label_ids > -1)[0])
        logger.info(f"# unique faces: {unique_faces_count}")

        result = defaultdict(lambda: [])
        for label in range(unique_faces_count):
            ids = np.where(labels == label)[0]
            for id in ids[:max_per_label]:
                image_path = encodings_data[id]["image_path"]
                image = cv2.imread(image_path)
                frame, _ = os.path.splitext(os.path.basename(image_path))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = self.crop_image(encodings_data[id]["loc"], image)
                result[label].append({"image": image, "frame": frame})
        return result

    def sample_input(self) -> Content:
        file_path = "sample.mp4"

        with open(file_path, "rb") as f:
            data = f.read()

        return Content(
            data=data,
            content_type="video/mp4",
            features=[Feature.metadata({"filename": file_path})],
        )


if __name__ == "__main__":
    contents = FaceExtractor().extract_sample_input()
    print(len(contents))
    for content in contents:
        print(len(content.features))
        for feature in content.features:
            print(feature.value)
