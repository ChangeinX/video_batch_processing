import argparse
import os
import time

import cv2
import numpy as np
import torch

import dropbox
from dropbox.files import WriteMode


class S3OpenCVSimpleTest:
    def __init__(self, file_id, access_token):
        """
        Constructor for S3OpenCVSimpleTest class
        :param file_id:
        :param access_token:
        """
        self.file_id = file_id
        self.access_token = access_token
        self.dbx = dropbox.Dropbox(access_token)
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """
        Load the Yolo v5 model
        :return: model
        """
        # load model
        model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
        return model

    def score(self, frame):
        """
        Run the Yolo v5 model on the frame
        :param frame: frame to run model on
        :return: frame with bounding boxes
        """
        self.model.to(self.device)
        # Frame is a numpy array
        frame = [frame]
        # Results is a tensor
        results = self.model(frame)
        # Labels and coordinates are numpy arrays
        labels, coordinates = (
            results.xyxyn[0][:, -1].cpu().numpy(),
            results.xyxyn[0][:, :-1].cpu().numpy(),
        )

        return labels, coordinates

    # def remove_unwanted_objects(self, frame, labels, coordinates):
    #     """
    #     Remove unwanted objects from the frame
    #     :param frame: frame to remove objects from
    #     :param labels: labels of objects in frame
    #     :param coordinates: coordinates of objects in frame
    #     :return: frame with unwanted objects removed
    #     """
    #     for label, coordinate in zip(labels, coordinates):
    #         if self.class_to_label(label) == "person":
    #             frame = np.zeros(frame.shape, dtype=np.uint8)
    #             cv2.putText(
    #                 frame,
    #                 f"Object Removed: {self.class_to_label(label)}",
    #                 (0, 0),
    #                 cv2.FONT_HERSHEY_SIMPLEX,
    #                 1,
    #                 (0, 0, 255),
    #                 2,
    #             )
    #     return frame

    def class_to_label(self, class_num):
        """
        For each class, return the label
        :param class_num: class number
        :return: label for class
        """
        return self.classes[int(class_num)]

    def plot_boxes(self, results, frame):
        """
        Plot the bounding boxes on the frame
        :param results: results from model
        :param frame: frame to plot boxes on
        :return: frame with boxes plotted
        """
        labels, coordinates = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = coordinates[i]
            if row[4] >= 0.5:
                x1, y1, x2, y2 = (
                    int(row[0] * x_shape),
                    int(row[1] * y_shape),
                    int(row[2] * x_shape),
                    int(row[3] * y_shape),
                )
                bgr = (0, 255, 0)
                if not np.all(frame == 0):
                    cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                    cv2.putText(
                        frame,
                        f"{self.class_to_label(labels[i])} {row[4]:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        bgr,
                        2,
                        cv2.LINE_AA,
                    )
        return frame

    def get_file_name(self):
        """
        Get the file name from the file id
        :return: file name
        """
        file_name = self.dbx.files_get_metadata(self.file_id).path_display
        return file_name[1:]

    def run(self):
        """
        Run the model on the video
        """
        # download video
        print("Downloading video...")
        # download path for video is root directory
        file_name = self.get_file_name()
        out_file = file_name.split(".")[0] + "_out.mp4"
        self.dbx.files_download_to_file(file_name, self.file_id)

        # read video
        print("Reading video...")
        cap = cv2.VideoCapture(file_name)

        # get video properties
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # create video writer
        out = cv2.VideoWriter(
            out_file,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (frame_width, frame_height),
        )

        # run model
        print("Running model...")
        start_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"Start time: {start_time}")
        while cap.isOpened():
            score_time = time.time()
            ret, frame = cap.read()
            if ret:
                labels, coordinates = self.score(frame)
                frame = self.plot_boxes((labels, coordinates), frame)
                out.write(frame)
                print(f"Frame processed: {cap.get(cv2.CAP_PROP_POS_FRAMES)}")
                # score time in milliseconds
                print(f"Score time: {1000 * (time.time() - score_time)}")
            else:
                break
        cap.release()
        out.release()

        print("Uploading video...")
        # upload video
        with open(out_file, "rb") as f:
            self.dbx.files_upload(f.read(), "/" + out_file, mode=WriteMode("overwrite"))

            print(f'End time: {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}')

        # remove video
        os.remove(file_name)
        os.remove(out_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_id", type=str, required=True)
    parser.add_argument("--access_token", type=str, required=True)
    args = parser.parse_args()
    video = S3OpenCVSimpleTest(args.file_id, args.access_token)
    try:
        video.run()
    except Exception as e:
        print(f"Error: {e}, PARAMS: {args}")
        raise e
