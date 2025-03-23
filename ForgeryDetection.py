from sklearn.cluster import DBSCAN
import numpy as np
import cv2

class Detect:
    def __init__(self, input=None):
        if input:
            self.image = cv2.imread(input)
        else:
            self.image = None
        self.descriptors = None
        self.key_points = None  # Ensure keypoints are initialized

    def siftDetector(self):
        if self.image is None:
            raise ValueError("Image not loaded. Provide a valid image path.")
        
        sift = cv2.SIFT_create()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.key_points, self.descriptors = sift.detectAndCompute(gray, None)

        if self.descriptors is None:
            raise ValueError("No keypoints detected. Image may not have enough features.")
        
        return self.key_points, self.descriptors

    def showSiftFeatures(self):
        if self.image is None or self.key_points is None:
            raise ValueError("Run siftDetector() first before calling showSiftFeatures().")
        
        sift_image = cv2.drawKeypoints(self.image, self.key_points, self.image.copy())
        return sift_image

    def locateForgery(self, eps=40, min_sample=2):
        if self.descriptors is None:
            raise ValueError("Descriptors not found. Run siftDetector() first.")
        
        clusters = DBSCAN(eps=eps, min_samples=min_sample).fit(self.descriptors)
        size = np.unique(clusters.labels_).shape[0] - 1
        
        if size == 0 and np.unique(clusters.labels_)[0] == -1:
            print("No Forgery Found!")
            return None

        if size == 0:
            size = 1

        cluster_list = [[] for _ in range(size)]
        for idx in range(len(self.key_points)):
            if clusters.labels_[idx] != -1:
                cluster_list[clusters.labels_[idx]].append(
                    (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1]))
                )

        forgery = self.image.copy()
        for points in cluster_list:
            if len(points) > 1:
                for idx1 in range(1, len(points)):
                    cv2.line(forgery, points[0], points[idx1], (0, 255, 0), 5)

        return forgery
