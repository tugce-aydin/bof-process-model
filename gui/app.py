import sys
import subprocess
from pathlib import Path

import joblib
import pandas as pd
import pyqtgraph as pg

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)

    PROJECT_DIR = BUNDLE_DIR
    MODEL_DIR = BUNDLE_DIR / "ml" / "models"
    EXECUTABLE = BUNDLE_DIR / "bof_model"

    RESULTS_DIR = Path.home() / "Documents" / "BOF Process Model" / "results"
else:
    PROJECT_DIR = Path(__file__).resolve().parents[1]
    MODEL_DIR = PROJECT_DIR / "ml" / "models"
    EXECUTABLE = PROJECT_DIR / "build" / "bof_model"
    RESULTS_DIR = PROJECT_DIR / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "hot_metal_kg",
    "scrap_kg",
    "initial_temp_C",
    "initial_C_pct",
    "initial_Si_pct",
    "initial_Mn_pct",
    "oxygen_flow_Nm3_min",
]


class BOFApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "BOF Process Model - Physics Simulation + ML Prediction"
        )

        self.time_model = joblib.load(
            MODEL_DIR / "endpoint_time_model.pkl"
        )

        self.temperature_model = joblib.load(
            MODEL_DIR / "endpoint_temperature_model.pkl"
        )

        self.history = None

        self.setup_style()
        self.setup_menu()
        self.setup_ui()
        self.setup_status_bar()

        self.showMaximized()

    def setup_style(self):

        self.setStyleSheet("""
            QMainWindow {
                background: #d4d0c8;
            }

            QWidget {
                font-family: Arial;
                font-size: 12px;
                color: #000000;
            }

            QTabWidget::pane {
                border: 1px solid #808080;
                background: #d4d0c8;
            }

            QTabBar::tab {
                background: #d4d0c8;
                border: 1px solid #808080;
                padding: 7px 15px;
                min-width: 90px;
            }

            QTabBar::tab:selected {
                background: #f0f0f0;
                font-weight: bold;
            }

            QGroupBox {
                border: 1px solid #808080;
                margin-top: 10px;
                padding-top: 8px;
                font-weight: bold;
                background: #d4d0c8;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #000080;
            }

            QDoubleSpinBox {
                background: white;
                border: 1px inset #808080;
                padding: 4px;
                min-height: 22px;
                color: black;
            }

            QPushButton {
                background: #d4d0c8;
                border: 2px outset #eeeeee;
                padding: 8px;
                font-weight: bold;
            }

            QPushButton:pressed {
                border: 2px inset #eeeeee;
            }

            QPushButton:disabled {
                color: #808080;
            }

            QMenuBar {
                background: #d4d0c8;
            }

            QMenuBar::item:selected {
                background: #000080;
                color: white;
            }

            QStatusBar {
                background: #d4d0c8;
                border-top: 1px solid #808080;
            }

            QTableWidget {
                background: white;
                gridline-color: #b0b0b0;
                alternate-background-color: #f2f2f2;
            }

            QHeaderView::section {
                background: #d4d0c8;
                border: 1px solid #808080;
                padding: 4px;
                font-weight: bold;
            }

            QTextEdit {
                background: white;
                border: 1px solid #808080;
                padding: 8px;
            }
        """)

    def setup_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        view_menu = menu.addMenu("View")
        help_menu = menu.addMenu("Help")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        maximize_action = QAction("Maximize", self)
        maximize_action.triggered.connect(self.showMaximized)
        view_menu.addAction(maximize_action)

        about_action = QAction("About BOF Process Model", self)
        about_action.triggered.connect(
            lambda: self.tabs.setCurrentWidget(self.about_tab)
        )
        help_menu.addAction(about_action)

    def setup_ui(self):

        self.tabs = QTabWidget()

        self.simulation_tab = QWidget()
        self.graphs_tab = QWidget()
        self.results_tab = QWidget()
        self.ml_tab = QWidget()
        self.about_tab = QWidget()

        self.tabs.addTab(self.simulation_tab, "Simulation")
        self.tabs.addTab(self.graphs_tab, "Process Graphs")
        self.tabs.addTab(self.results_tab, "Results Table")
        self.tabs.addTab(self.ml_tab, "ML Analysis")
        self.tabs.addTab(self.about_tab, "About")

        self.setCentralWidget(self.tabs)

        self.build_simulation_tab()
        self.build_graphs_tab()
        self.build_results_tab()
        self.build_ml_tab()
        self.build_about_tab()

    def build_simulation_tab(self):

        root = QHBoxLayout(self.simulation_tab)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        left = self.create_input_section()
        right = self.create_main_section()

        left.setFixedWidth(350)

        root.addWidget(left)
        root.addWidget(right, 1)

    def create_input_section(self):

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        process_group = QGroupBox("Process Inputs")
        process_layout = QVBoxLayout(process_group)

        charge = QGroupBox("Charge")
        charge_layout = QGridLayout(charge)

        self.hot_metal = self.create_spin(
            90000, 110000, 100000, 0
        )

        self.scrap = self.create_spin(
            10000, 20000, 15000, 0
        )

        charge_layout.addWidget(
            QLabel("Hot metal mass:"), 0, 0
        )
        charge_layout.addWidget(
            self.hot_metal, 0, 1
        )
        charge_layout.addWidget(
            QLabel("kg"), 0, 2
        )

        charge_layout.addWidget(
            QLabel("Scrap mass:"), 1, 0
        )
        charge_layout.addWidget(
            self.scrap, 1, 1
        )
        charge_layout.addWidget(
            QLabel("kg"), 1, 2
        )

        process_layout.addWidget(charge)

        conditions = QGroupBox("Initial Conditions")
        conditions_layout = QGridLayout(conditions)

        self.temperature = self.create_spin(
            1300, 1400, 1350, 0
        )

        self.carbon = self.create_spin(
            4.0, 5.0, 4.5, 2
        )

        self.silicon = self.create_spin(
            0.3, 0.7, 0.5, 2
        )

        self.manganese = self.create_spin(
            0.2, 0.6, 0.4, 2
        )

        fields = [
            (
                "Initial temperature:",
                self.temperature,
                "°C",
            ),
            (
                "Carbon (C):",
                self.carbon,
                "wt.%",
            ),
            (
                "Silicon (Si):",
                self.silicon,
                "wt.%",
            ),
            (
                "Manganese (Mn):",
                self.manganese,
                "wt.%",
            ),
        ]

        for row, (name, widget, unit) in enumerate(fields):

            conditions_layout.addWidget(
                QLabel(name), row, 0
            )

            conditions_layout.addWidget(
                widget, row, 1
            )

            conditions_layout.addWidget(
                QLabel(unit), row, 2
            )

        process_layout.addWidget(conditions)

        oxygen_group = QGroupBox("Oxygen Blowing")
        oxygen_layout = QGridLayout(oxygen_group)

        self.oxygen = self.create_spin(
            250, 350, 300, 0
        )

        oxygen_layout.addWidget(
            QLabel("Oxygen flow rate:"), 0, 0
        )

        oxygen_layout.addWidget(
            self.oxygen, 0, 1
        )

        oxygen_layout.addWidget(
            QLabel("Nm³/min"), 0, 2
        )

        process_layout.addWidget(oxygen_group)

        buttons = QHBoxLayout()

        self.run_button = QPushButton(
            "▶  Run Simulation"
        )

        self.run_button.clicked.connect(
            self.run_simulation
        )

        self.stop_button = QPushButton(
            "■  Stop"
        )

        self.stop_button.setEnabled(False)

        buttons.addWidget(self.run_button)
        buttons.addWidget(self.stop_button)

        process_layout.addLayout(buttons)

        layout.addWidget(process_group)

        info = QGroupBox("Simulation Info")
        info_layout = QGridLayout(info)

        self.info_status = QLabel("Ready")
        self.info_status.setStyleSheet(
            "color: green; font-weight: bold;"
        )

        self.simulation_time_label = QLabel("-")

        info_rows = [
            (
                "Status:",
                self.info_status,
            ),
            (
                "Simulation time:",
                self.simulation_time_label,
            ),
            (
                "Time step:",
                QLabel("1 s"),
            ),
            (
                "Physics model:",
                QLabel("C++"),
            ),
            (
                "ML model:",
                QLabel("Linear Regression"),
            ),
            (
                "Training data:",
                QLabel("1000 simulations"),
            ),
        ]

        for row, (name, value) in enumerate(info_rows):

            info_layout.addWidget(
                QLabel(name), row, 0
            )

            info_layout.addWidget(
                value, row, 1
            )

        layout.addWidget(info)
        layout.addStretch()

        return container

    def create_spin(
        self,
        minimum,
        maximum,
        value,
        decimals,
    ):

        box = QDoubleSpinBox()

        box.setRange(minimum, maximum)
        box.setValue(value)
        box.setDecimals(decimals)

        return box

    def create_main_section(self):

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        results_group = QGroupBox("Results Summary")
        results_layout = QHBoxLayout(results_group)

        self.physics_panel = self.create_result_panel(
            "Physics Model (C++)",
            "#dbe9f8",
        )

        self.ml_panel = self.create_result_panel(
            "ML Surrogate (Linear Regression)",
            "#e0f2df",
        )

        self.difference_panel = (
            self.create_difference_panel()
        )

        results_layout.addWidget(
            self.physics_panel["frame"]
        )

        results_layout.addWidget(
            self.ml_panel["frame"]
        )

        results_layout.addWidget(
            self.difference_panel["frame"]
        )

        layout.addWidget(results_group)

        graphs_group = QGroupBox("Process Graphs")
        graph_layout = QGridLayout(graphs_group)

        self.composition_plot = self.create_plot(
            "Composition vs Time",
            "Composition",
            "wt.%",
        )

        self.temperature_plot = self.create_plot(
            "Bath Temperature vs Time",
            "Temperature",
            "°C",
        )

        self.scrap_plot = self.create_plot(
            "Scrap Melting",
            "Melted scrap",
            "kg",
        )

        self.products_plot = self.create_plot(
            "Products Formation",
            "Mass",
            "kg",
        )

        graph_layout.addWidget(
            self.composition_plot, 0, 0
        )

        graph_layout.addWidget(
            self.temperature_plot, 0, 1
        )

        graph_layout.addWidget(
            self.scrap_plot, 1, 0
        )

        graph_layout.addWidget(
            self.products_plot, 1, 1
        )

        graph_layout.setRowStretch(0, 1)
        graph_layout.setRowStretch(1, 1)
        graph_layout.setColumnStretch(0, 1)
        graph_layout.setColumnStretch(1, 1)

        layout.addWidget(graphs_group, 1)

        return container

    def create_result_panel(
        self,
        title,
        background,
    ):

        frame = QFrame()

        frame.setStyleSheet(f"""
            QFrame {{
                background: {background};
                border: 1px solid #808080;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QGridLayout(frame)

        heading = QLabel(title)

        heading.setStyleSheet(
            "font-weight: bold; font-size: 13px;"
        )

        time_value = QLabel("—")
        temp_value = QLabel("—")

        metric_font = QFont()
        metric_font.setPointSize(17)
        metric_font.setBold(True)

        time_value.setFont(metric_font)
        temp_value.setFont(metric_font)

        layout.addWidget(
            heading, 0, 0, 1, 2
        )

        layout.addWidget(
            QLabel("Endpoint time:"),
            1,
            0,
        )

        layout.addWidget(
            time_value,
            1,
            1,
        )

        layout.addWidget(
            QLabel("Endpoint temperature:"),
            2,
            0,
        )

        layout.addWidget(
            temp_value,
            2,
            1,
        )

        return {
            "frame": frame,
            "time": time_value,
            "temperature": temp_value,
        }

    def create_difference_panel(self):

        frame = QFrame()

        frame.setStyleSheet("""
            QFrame {
                background: #eeeeee;
                border: 1px solid #808080;
            }

            QLabel {
                background: transparent;
                border: none;
            }
        """)

        layout = QGridLayout(frame)

        heading = QLabel(
            "Difference (ML - Physics)"
        )

        heading.setStyleSheet(
            "font-weight: bold;"
        )

        self.delta_time = QLabel("—")
        self.delta_temp = QLabel("—")

        layout.addWidget(
            heading,
            0,
            0,
            1,
            2,
        )

        layout.addWidget(
            QLabel("Δ time:"),
            1,
            0,
        )

        layout.addWidget(
            self.delta_time,
            1,
            1,
        )

        layout.addWidget(
            QLabel("Δ temperature:"),
            2,
            0,
        )

        layout.addWidget(
            self.delta_temp,
            2,
            1,
        )

        layout.setRowStretch(3, 1)

        return {
            "frame": frame
        }

    def create_plot(
        self,
        title,
        ylabel,
        unit,
    ):

        plot = pg.PlotWidget()

        plot.setBackground("w")

        plot.setTitle(
            title,
            color="k",
            size="11pt",
        )

        plot.setLabel(
            "bottom",
            "Time",
            units="s",
            color="k",
        )

        plot.setLabel(
            "left",
            ylabel,
            units=unit,
            color="k",
        )

        plot.showGrid(
            x=True,
            y=True,
            alpha=0.25,
        )

        plot.getAxis(
            "bottom"
        ).setTextPen("k")

        plot.getAxis(
            "left"
        ).setTextPen("k")

        return plot

    def run_simulation(self):

        self.run_button.setEnabled(False)

        self.info_status.setText("Running...")

        self.info_status.setStyleSheet(
            "color: #b36b00; font-weight: bold;"
        )

        self.statusBar().showMessage(
            "Running C++ physics model "
            "and ML surrogate..."
        )

        QApplication.processEvents()

        hot_metal = self.hot_metal.value()
        scrap = self.scrap.value()
        temperature = self.temperature.value()
        carbon = self.carbon.value()
        silicon = self.silicon.value()
        manganese = self.manganese.value()
        oxygen = self.oxygen.value()

        input_data = pd.DataFrame(
            [[
                hot_metal,
                scrap,
                temperature,
                carbon,
                silicon,
                manganese,
                oxygen,
            ]],
            columns=FEATURES,
        )

        try:

            predicted_time = (
                self.time_model.predict(
                    input_data
                )[0]
            )

            predicted_temperature = (
                self.temperature_model.predict(
                    input_data
                )[0]
            )

            executable = EXECUTABLE

            output_csv = (
                RESULTS_DIR
                / "gui_simulation.csv"
            )

            command = [
                str(executable),
                "--simulate",
                str(hot_metal),
                str(scrap),
                str(temperature),
                str(carbon),
                str(silicon),
                str(manganese),
                str(oxygen),
                "0.06",
                str(output_csv),
            ]

            result = subprocess.run(
                command,
                cwd=RESULTS_DIR,
                capture_output=True,
                text=True,
                check=True,
            )

            gui_line = None

            for line in result.stdout.splitlines():

                if line.startswith(
                    "GUI_RESULT,"
                ):
                    gui_line = line
                    break

            if gui_line is None:

                raise RuntimeError(
                    "C++ model did not return "
                    "GUI_RESULT."
                )

            values = gui_line.split(",")

            if len(values) < 10:

                raise RuntimeError(
                    "Invalid GUI_RESULT returned "
                    "by C++ model."
                )

            endpoint_reached = int(
                values[1]
            )

            physics_time = float(
                values[2]
            )

            physics_temperature = float(
                values[3]
            )

            final_carbon = float(
                values[4]
            )

            final_silicon = float(
                values[5]
            )

            final_manganese = float(
                values[6]
            )

            melted_scrap = float(
                values[7]
            )

            total_co = float(
                values[8]
            )

            total_slag = float(
                values[9]
            )

            if endpoint_reached != 1:

                raise RuntimeError(
                    "Target carbon endpoint "
                    "was not reached."
                )

            self.physics_panel[
                "time"
            ].setText(
                f"{physics_time:.1f} s"
            )

            self.physics_panel[
                "temperature"
            ].setText(
                f"{physics_temperature:.1f} °C"
            )

            self.ml_panel[
                "time"
            ].setText(
                f"{predicted_time:.1f} s"
            )

            self.ml_panel[
                "temperature"
            ].setText(
                f"{predicted_temperature:.1f} °C"
            )

            delta_time = (
                predicted_time
                - physics_time
            )

            delta_temperature = (
                predicted_temperature
                - physics_temperature
            )

            self.delta_time.setText(
                f"{delta_time:+.1f} s"
            )

            self.delta_temp.setText(
                f"{delta_temperature:+.1f} °C"
            )

            self.simulation_time_label.setText(
                f"{physics_time:.0f} s"
            )

            self.history = pd.read_csv(
                output_csv
            )

            self.plot_results(
                self.history
            )

            self.update_large_graphs(
                self.history
            )

            self.update_results_table(
                self.history
            )

            self.update_summary(
                final_carbon,
                final_silicon,
                final_manganese,
                melted_scrap,
                total_co,
                total_slag,
                physics_time,
                physics_temperature,
                predicted_time,
                predicted_temperature,
            )

            self.info_status.setText(
                "Completed"
            )

            self.info_status.setStyleSheet(
                "color: green; font-weight: bold;"
            )

            self.statusBar().showMessage(
                f"Simulation complete | "
                f"Final C: "
                f"{final_carbon:.4f} wt.% | "
                f"Si: "
                f"{final_silicon:.4f} wt.% | "
                f"Mn: "
                f"{final_manganese:.4f} wt.% | "
                f"Melted scrap: "
                f"{melted_scrap:.0f} kg | "
                f"CO: {total_co:.0f} kg | "
                f"Slag: {total_slag:.0f} kg"
            )

        except Exception as error:

            self.info_status.setText(
                "Error"
            )

            self.info_status.setStyleSheet(
                "color: red; font-weight: bold;"
            )

            self.statusBar().showMessage(
                f"Simulation error: {error}"
            )

            print(
                f"Simulation error: {error}"
            )

        finally:

            self.run_button.setEnabled(
                True
            )

    def plot_results(self, data):

        time = data["time_s"]

        self.composition_plot.clear()
        self.temperature_plot.clear()
        self.scrap_plot.clear()
        self.products_plot.clear()

        if (
            self.composition_plot
            .plotItem
            .legend
            is None
        ):
            self.composition_plot.addLegend()

        self.composition_plot.plot(
            time,
            data["carbon_wt_pct"],
            pen=pg.mkPen(
                "#cc0000",
                width=2,
            ),
            name="C",
        )

        self.composition_plot.plot(
            time,
            data["silicon_wt_pct"],
            pen=pg.mkPen(
                "#0055aa",
                width=2,
            ),
            name="Si",
        )

        self.composition_plot.plot(
            time,
            data["manganese_wt_pct"],
            pen=pg.mkPen(
                "#008000",
                width=2,
            ),
            name="Mn",
        )

        self.temperature_plot.plot(
            time,
            data["temperature_C"],
            pen=pg.mkPen(
                "#cc0000",
                width=2,
            ),
        )

        self.scrap_plot.plot(
            time,
            data["melted_scrap_kg"],
            pen=pg.mkPen(
                "#660099",
                width=2,
            ),
        )

        if (
            self.products_plot
            .plotItem
            .legend
            is None
        ):
            self.products_plot.addLegend()

        self.products_plot.plot(
            time,
            data["CO_kg"],
            pen=pg.mkPen(
                "#202020",
                width=2,
            ),
            name="CO",
        )

        self.products_plot.plot(
            time,
            data["slag_kg"],
            pen=pg.mkPen(
                "#cc6600",
                width=2,
            ),
            name="Slag",
        )

        plots = [
            self.composition_plot,
            self.temperature_plot,
            self.scrap_plot,
            self.products_plot,
        ]

        for plot in plots:
            plot.enableAutoRange()

    def build_graphs_tab(self):

        layout = QGridLayout(
            self.graphs_tab
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        self.large_composition_plot = (
            self.create_plot(
                "Composition vs Time",
                "Composition",
                "wt.%",
            )
        )

        self.large_temperature_plot = (
            self.create_plot(
                "Bath Temperature vs Time",
                "Temperature",
                "°C",
            )
        )

        self.large_scrap_plot = (
            self.create_plot(
                "Scrap Melting",
                "Melted scrap",
                "kg",
            )
        )

        self.large_products_plot = (
            self.create_plot(
                "Products Formation",
                "Mass",
                "kg",
            )
        )

        layout.addWidget(
            self.large_composition_plot,
            0,
            0,
        )

        layout.addWidget(
            self.large_temperature_plot,
            0,
            1,
        )

        layout.addWidget(
            self.large_scrap_plot,
            1,
            0,
        )

        layout.addWidget(
            self.large_products_plot,
            1,
            1,
        )

        layout.setRowStretch(
            0,
            1,
        )

        layout.setRowStretch(
            1,
            1,
        )

        layout.setColumnStretch(
            0,
            1,
        )

        layout.setColumnStretch(
            1,
            1,
        )

    def update_large_graphs(
        self,
        data,
    ):

        time = data["time_s"]

        plots = [
            self.large_composition_plot,
            self.large_temperature_plot,
            self.large_scrap_plot,
            self.large_products_plot,
        ]

        for plot in plots:
            plot.clear()

        if (
            self.large_composition_plot
            .plotItem
            .legend
            is None
        ):
            self.large_composition_plot.addLegend()

        self.large_composition_plot.plot(
            time,
            data["carbon_wt_pct"],
            pen=pg.mkPen(
                "#cc0000",
                width=2,
            ),
            name="C",
        )

        self.large_composition_plot.plot(
            time,
            data["silicon_wt_pct"],
            pen=pg.mkPen(
                "#0055aa",
                width=2,
            ),
            name="Si",
        )

        self.large_composition_plot.plot(
            time,
            data["manganese_wt_pct"],
            pen=pg.mkPen(
                "#008000",
                width=2,
            ),
            name="Mn",
        )

        self.large_temperature_plot.plot(
            time,
            data["temperature_C"],
            pen=pg.mkPen(
                "#cc0000",
                width=2,
            ),
        )

        self.large_scrap_plot.plot(
            time,
            data["melted_scrap_kg"],
            pen=pg.mkPen(
                "#660099",
                width=2,
            ),
        )

        if (
            self.large_products_plot
            .plotItem
            .legend
            is None
        ):
            self.large_products_plot.addLegend()

        self.large_products_plot.plot(
            time,
            data["CO_kg"],
            pen=pg.mkPen(
                "#202020",
                width=2,
            ),
            name="CO",
        )

        self.large_products_plot.plot(
            time,
            data["slag_kg"],
            pen=pg.mkPen(
                "#cc6600",
                width=2,
            ),
            name="Slag",
        )

        for plot in plots:
            plot.enableAutoRange()

    def build_results_tab(self):

        layout = QVBoxLayout(
            self.results_tab
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        summary_group = QGroupBox(
            "Latest Simulation Summary"
        )

        summary_layout = QVBoxLayout(
            summary_group
        )

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)

        self.summary_text.setPlainText(
            "No simulation has been run yet."
        )

        summary_layout.addWidget(
            self.summary_text
        )

        layout.addWidget(
            summary_group
        )

        table_group = QGroupBox(
            "Process History"
        )

        table_layout = QVBoxLayout(
            table_group
        )

        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(
            True
        )

        table_layout.addWidget(
            self.results_table
        )

        layout.addWidget(
            table_group,
            1,
        )

    def update_results_table(
        self,
        data,
    ):

        self.results_table.clear()

        self.results_table.setColumnCount(
            len(data.columns)
        )

        self.results_table.setRowCount(
            len(data)
        )

        self.results_table.setHorizontalHeaderLabels(
            list(data.columns)
        )

        for row in range(
            len(data)
        ):

            for column in range(
                len(data.columns)
            ):

                value = data.iloc[
                    row,
                    column,
                ]

                item = QTableWidgetItem(
                    f"{value:.6g}"
                    if isinstance(
                        value,
                        float,
                    )
                    else str(value)
                )

                self.results_table.setItem(
                    row,
                    column,
                    item,
                )

        self.results_table.resizeColumnsToContents()

    def update_summary(
        self,
        final_carbon,
        final_silicon,
        final_manganese,
        melted_scrap,
        total_co,
        total_slag,
        physics_time,
        physics_temperature,
        predicted_time,
        predicted_temperature,
    ):

        delta_time = (
            predicted_time
            - physics_time
        )

        delta_temperature = (
            predicted_temperature
            - physics_temperature
        )

        text = (
            "BOF PROCESS MODEL - LATEST RUN\n"
            "========================================\n\n"

            "PHYSICS MODEL\n"
            f"Endpoint time: {physics_time:.1f} s\n"
            f"Endpoint temperature: "
            f"{physics_temperature:.2f} °C\n"
            f"Final carbon: "
            f"{final_carbon:.5f} wt.%\n"
            f"Final silicon: "
            f"{final_silicon:.5f} wt.%\n"
            f"Final manganese: "
            f"{final_manganese:.5f} wt.%\n"
            f"Melted scrap: "
            f"{melted_scrap:.1f} kg\n"
            f"CO produced: "
            f"{total_co:.1f} kg\n"
            f"Simplified slag: "
            f"{total_slag:.1f} kg\n\n"

            "ML SURROGATE\n"
            f"Predicted endpoint time: "
            f"{predicted_time:.1f} s\n"
            f"Predicted endpoint temperature: "
            f"{predicted_temperature:.2f} °C\n\n"

            "ML - PHYSICS DIFFERENCE\n"
            f"Time difference: "
            f"{delta_time:+.1f} s\n"
            f"Temperature difference: "
            f"{delta_temperature:+.2f} °C\n"
        )

        self.summary_text.setPlainText(
            text
        )

    def build_ml_tab(self):

        layout = QVBoxLayout(
            self.ml_tab
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        performance = QGroupBox(
            "Surrogate Model Performance"
        )

        performance_layout = QVBoxLayout(
            performance
        )

        performance_text = QTextEdit()
        performance_text.setReadOnly(True)

        performance_text.setPlainText(
            "MACHINE LEARNING SURROGATE\n"
            "========================================\n\n"

            "Training dataset:\n"
            "1000 synthetic BOF simulations generated "
            "by the C++ physics model.\n\n"

            "Algorithms evaluated:\n"
            "- Linear Regression\n"
            "- Random Forest Regression\n\n"

            "Selected model:\n"
            "Linear Regression\n\n"

            "ENDPOINT TIME\n"
            "MAE:  9.731 s\n"
            "RMSE: 12.736 s\n"
            "R²:   0.9894\n"
            "5-fold CV R²: 0.9910\n\n"

            "ENDPOINT TEMPERATURE\n"
            "MAE:  2.152 °C\n"
            "RMSE: 2.923 °C\n"
            "R²:   0.9983\n"
            "5-fold CV R²: 0.9982\n\n"

            "Important:\n"
            "The ML surrogate reproduces the behaviour "
            "of the simplified C++ physics model. "
            "It is not trained or validated using "
            "industrial plant data."
        )

        performance_layout.addWidget(
            performance_text
        )

        layout.addWidget(
            performance
        )

        effects = QGroupBox(
            "Feature Effects"
        )

        effects_layout = QHBoxLayout(
            effects
        )

        time_effects = QTextEdit()
        time_effects.setReadOnly(True)

        time_effects.setPlainText(
            "ENDPOINT TIME\n"
            "Standardized effects\n\n"
            "Oxygen flow       -96.48\n"
            "Hot metal mass    +57.33\n"
            "Initial carbon    +51.93\n"
            "Initial silicon   +18.41\n"
            "Initial manganese  +4.16\n"
            "Scrap mass         +1.81\n"
            "Initial temp.      +0.46\n\n"
            "Negative oxygen-flow effect means that "
            "higher oxygen flow reduces endpoint time."
        )

        temperature_effects = QTextEdit()
        temperature_effects.setReadOnly(
            True
        )

        temperature_effects.setPlainText(
            "ENDPOINT TEMPERATURE\n"
            "Standardized effects\n\n"
            "Scrap mass        -46.07\n"
            "Initial silicon   +35.74\n"
            "Initial temp.     +26.45\n"
            "Initial carbon    +21.17\n"
            "Hot metal mass    +13.74\n"
            "Oxygen flow        +7.62\n"
            "Initial manganese  +6.38\n\n"
            "The signs describe relationships learned "
            "from the C++ simulator dataset."
        )

        effects_layout.addWidget(
            time_effects
        )

        effects_layout.addWidget(
            temperature_effects
        )

        layout.addWidget(
            effects,
            1,
        )

    def build_about_tab(self):

        layout = QVBoxLayout(
            self.about_tab
        )

        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        group = QGroupBox(
            "About BOF Dynamic Process Model"
        )

        group_layout = QVBoxLayout(
            group
        )

        text = QTextEdit()
        text.setReadOnly(True)

        text.setPlainText(
            "BOF DYNAMIC PROCESS MODEL\n"
            "========================================\n\n"

            "Educational engineering software for "
            "simulating a simplified Basic Oxygen "
            "Furnace steelmaking process.\n\n"

            "Architecture\n"
            "----------------------------------------\n"
            "C++\n"
            "Physics-based dynamic process model\n\n"
            "Python / scikit-learn\n"
            "Machine-learning surrogate models\n\n"
            "PySide6 / PyQtGraph\n"
            "Desktop user interface and interactive "
            "process visualization\n\n"

            "Model scope\n"
            "----------------------------------------\n"
            "- Carbon oxidation\n"
            "- Silicon oxidation\n"
            "- Manganese oxidation\n"
            "- Oxygen allocation\n"
            "- Simplified mass balance\n"
            "- Simplified energy balance\n"
            "- Scrap heating and melting\n"
            "- CO formation\n"
            "- Simplified slag formation\n"
            "- Carbon endpoint detection\n"
            "- ML endpoint-time prediction\n"
            "- ML endpoint-temperature prediction\n\n"

            "Model limitations\n"
            "----------------------------------------\n"
            "This model is an educational engineering "
            "model and is not intended to reproduce an "
            "industrial BOF Level-2 process model.\n\n"

            "The temperature calculation is an "
            "uncalibrated engineering estimate.\n\n"

            "The model does not include detailed slag "
            "chemistry, Fe/FeO reactions, phosphorus "
            "or sulfur refining, CFD, detailed reaction "
            "kinetics, refractory heat-transfer models, "
            "or industrial process-control logic.\n\n"

            "Machine-learning models are trained on "
            "synthetic data generated by this simulator, "
            "not on real steel-plant data."
        )

        group_layout.addWidget(
            text
        )

        layout.addWidget(
            group
        )

    def setup_status_bar(self):

        status = QStatusBar()

        self.setStatusBar(
            status
        )

        status.showMessage(
            "Ready"
        )


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    app.setStyle(
        "Fusion"
    )

    window = BOFApp()

    window.show()

    sys.exit(
        app.exec()
    )