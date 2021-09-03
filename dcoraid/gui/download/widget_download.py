import os.path as os_path
import pkg_resources

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtCore import QStandardPaths

from ...download import DownloadQueue

from ..api import get_ckan_api


class DownloadWidget(QtWidgets.QWidget):
    download_finished = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        """Manage running downloads
        """
        super(DownloadWidget, self).__init__(*args, **kwargs)
        path_ui = pkg_resources.resource_filename(
            "dcoraid.gui.download", "widget_download.ui")
        uic.loadUi(path_ui, self)

        # use a persistent shelf to be able to resume uploads on startup
        shelf_path = os_path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.AppLocalDataLocation),
            "persistent_download_jobs")

        self.jobs = DownloadQueue(api=get_ckan_api(),
                                  path_persistent_job_list=shelf_path)
        self.widget_jobs.set_job_list(self.jobs)

    @QtCore.pyqtSlot(str)
    def download_resource(self, resource_id):
        dl_path = QStandardPaths.writableLocation(
                      QStandardPaths.DownloadLocation)
        self.widget_jobs.jobs.new_job(resource_id, dl_path)


class DownloadTableWidget(QtWidgets.QTableWidget):
    download_finished = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(DownloadTableWidget, self).__init__(*args, **kwargs)
        self.jobs = []  # Will become DownloadQueue with self.set_job_list

        settings = QtCore.QSettings()
        if bool(int(settings.value("debug/without timers", "0"))):
            self.timer = None
        else:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_job_status)
            self.timer.start(30)
        self._finished_downloads = []

    def set_job_list(self, jobs):
        """Set the current job list

        The job list can be a `list`, but it is actually
        a `DownloadQueue`.
        """
        # This is the actual initialization
        self.jobs = jobs

    def on_job_abort(self, resource_id):
        self.jobs.abort_job(resource_id)

    def on_job_delete(self, resource_id):
        self.jobs.remove_job(resource_id)

    def on_download_finished(self, resource_id):
        """Triggers download_finished whenever a download is finished"""
        if resource_id not in self._finished_downloads:
            self._finished_downloads.append(resource_id)
            self.jobs.jobs_eternal.set_job_done(resource_id)
            self.download_finished.emit()

    @QtCore.pyqtSlot()
    def update_job_status(self):
        """Update UI with information from self.jobs (DownloadJobList)"""
        # disable updates
        self.setUpdatesEnabled(False)
        # make sure the length of the table is long enough
        self.setRowCount(len(self.jobs))
        self.setColumnCount(6)

        for row, job in enumerate(self.jobs):
            status = job.get_status()
            self.set_label_item(row, 0, job.resource_id[:5])
            try:
                title = get_download_title(job)
            except BaseException:
                # Probably a connection error
                title = "-- error getting dataset title --"
            self.set_label_item(row, 1, title)
            self.set_label_item(row, 2, status["state"])
            self.set_label_item(row, 3, job.get_progress_string())
            self.set_label_item(row, 4, job.get_rate_string())
            if status["state"] == "done":
                self.on_download_finished(job.resource_id)
            self.set_actions_item(row, 5, job)

        # spacing (did not work in __init__)
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # enable updates again
        self.setUpdatesEnabled(True)

    def set_label_item(self, row, col, label):
        """Get/Create a Qlabel at the specified position

        User has to make sure that row and column count are set
        """
        label = "{}".format(label)
        item = self.item(row, col)
        if item is None:
            item = QtWidgets.QTableWidgetItem(label)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.setItem(row, col, item)
        else:
            if item.text() != label:
                item.setText(label)

    def set_actions_item(self, row, col, job):
        """Set/Create a TableCellActions widget in the table

        Refreshes the widget and also connects signals.
        """
        wid = self.cellWidget(row, col)
        if wid is None:
            pass
            # add actions for open directory, view resource online, delete
            # wid = TableCellActions(job)
            # wid.delete_job.connect(self.on_job_delete)
            # wid.abort_job.connect(self.on_job_abort)
            # self.setCellWidget(row, col, wid)
        # wid.refresh_visibility(job)


def get_download_title(job):
    res_dict = job.get_resource_dict()
    ds_dict = job.get_dataset_dict()
    title = ds_dict.get("title")
    if not title:
        title = ds_dict.get("name")
    return f"{res_dict['name']} [{title}]"
