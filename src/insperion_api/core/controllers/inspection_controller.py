import asyncio
import os
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from insperion_api.settings.config import settings


class InspectionController:
    """
    Encapsulates the YOLO model and all related processing logic.
    """

    MODEL_PATH = Path(settings.yolo_model_path)

    def __init__(self):
        # Load the model once during initialization
        if not self.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {self.MODEL_PATH} {os.getcwd()}, {','.join(os.listdir(os.getcwd()))}"
            )
        self.model = YOLO(self.MODEL_PATH)

    def _decode_image(self, data: bytes) -> np.ndarray:
        """Decodes raw image bytes into an OpenCV image (frame)."""
        img_np = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        return frame

    def _format_results(self, results) -> dict:
        """Formats the raw YOLO results into a serializable JSON dictionary."""
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                # Get coordinates, class, and confidence
                xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                conf = box.conf[0].cpu().numpy()
                cls_id = int(box.cls[0].cpu().numpy())

                detections.append(
                    {
                        "class_id": cls_id,
                        "class_name": self.model.names[cls_id],
                        "confidence": float(conf),
                        "box": [
                            float(xyxy[0]),
                            float(xyxy[1]),
                            float(xyxy[2]),
                            float(xyxy[3]),
                        ],
                    }
                )
        return {"detections": detections}

    def _run_inference_sync(self, frame: np.ndarray):
        """
        Synchronous (blocking) inference call.
        This is separated to be run in a thread pool.
        """
        return self.model(frame, verbose=False)  # Run YOLO detection

    async def inspect(self, data: bytes) -> dict:
        """
        The main async processing pipeline for a single image.
        """
        # 1. Decode Image
        frame = self._decode_image(data)

        # 2. Run Inference in a separate thread to avoid blocking
        #    the main async event loop.
        results = await asyncio.to_thread(self._run_inference_sync, frame)

        # 3. Format Results
        detections_json = self._format_results(results)

        return detections_json
