from qgis.PyQt.QtWidgets import (
    QDockWidget, QLabel, QLineEdit, QPushButton, QSlider,
    QVBoxLayout, QHBoxLayout, QWidget
)
from qgis.PyQt.QtCore import QTimer, Qt
from qgis.core import (
    QgsProject, QgsGeometry, QgsPointXY, QgsVectorLayer,
    QgsFeature, QgsField
)

class WUSimulatorPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.dock = None

    def initGui(self):
        self.dock = QDockWidget("WU-Simulator", self.iface.mainWindow())
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self.id_label = QLabel("Work Unit ID:")
        self.id_input = QLineEdit()

        self.speed_label = QLabel("Speed: 800 ms")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(100)
        self.speed_slider.setMaximum(2000)
        self.speed_slider.setValue(800)
        self.speed_slider.setTickInterval(100)

        self.start_forward_btn = QPushButton("▶ Start Forward")
        self.start_backward_btn = QPushButton("◀ Start Backward")
        self.pause_btn = QPushButton("⏸ Pause")
        self.resume_btn = QPushButton("▶ Resume")
        self.stop_btn = QPushButton("⏹ Stop")

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.id_input)
        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_slider)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_forward_btn)
        btn_layout.addWidget(self.start_backward_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.stop_btn)
        self.layout.addLayout(btn_layout)

        self.widget.setLayout(self.layout)
        self.dock.setWidget(self.widget)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

        self.delay = 800
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance_animation)
        self.smooth_points = []
        self.idx = 0
        self.direction = 1
        self.is_paused = False

        self.start_forward_btn.clicked.connect(lambda: self.start_animation(forward=True))
        self.start_backward_btn.clicked.connect(lambda: self.start_animation(forward=False))
        self.pause_btn.clicked.connect(lambda: self.timer.stop())
        self.resume_btn.clicked.connect(lambda: self.timer.start(self.delay))
        self.stop_btn.clicked.connect(self.stop_animation)

    def update_speed(self, val):
        self.delay = val
        self.speed_label.setText(f"Speed: {val} ms")
        if self.timer.isActive():
            self.timer.setInterval(val)

    def start_animation(self, forward=True):
        self.timer.stop()
        self.direction = 1 if forward else -1
        work_unit_id = self.id_input.text().strip()

        try:
            work_unit_id = int(work_unit_id)
        except ValueError:
            self.iface.messageBar().pushWarning("WU-Simulator", "Invalid Work Unit ID")
            return

        layer = QgsProject.instance().mapLayersByName("Work Units")
        if not layer:
            self.iface.messageBar().pushWarning("WU-Simulator", "Layer 'Work Units' not found")
            return

        feature = next((f for f in layer[0].getFeatures() if f["work_unit_id"] == work_unit_id), None)
        if not feature:
            self.iface.messageBar().pushWarning("WU-Simulator", f"Feature {work_unit_id} not found")
            return

        geom = feature.geometry()
        self.smooth_points = self.interpolate_line_geometry(geom)
        self.idx = 0 if forward else len(self.smooth_points) - 1
        self.timer.start(self.delay)

    def stop_animation(self):
        self.timer.stop()
        self.idx = 0

    def advance_animation(self):
        if not self.smooth_points:
            return
        if 0 <= self.idx < len(self.smooth_points):
            self.canvas.setCenter(self.smooth_points[self.idx])
            self.canvas.refresh()
            self.idx += self.direction
        else:
            self.timer.stop()

    def interpolate_line_geometry(self, geometry, interval=0.0001):
        if geometry.isEmpty():
            raise ValueError("Null geometry")
        length = geometry.length()
        num_points = max(2, int(length / interval))
        return [QgsPointXY(geometry.interpolate(d).asPoint()) for d in [i * length / num_points for i in range(num_points + 1)]]

    def unload(self):
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock = None
