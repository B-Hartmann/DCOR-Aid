from functools import partial
import webbrowser

from ..api import get_ckan_api

from . import filter_base


class FilterCircles(filter_base.FilterBase):
    def __init__(self, *args, **kwargs):
        super(FilterCircles, self).__init__(*args, **kwargs)
        self.label.setText("Circles")
        self.lineEdit.setPlaceholderText("filter names...")
        self.checkBox.setVisible(False)

    def get_entry_actions(self, row, entry):
        api = get_ckan_api()
        url = f"{api.server}/organization/{entry['name']}"
        actions = [
            {"icon": "eye",
             "tooltip": f"view circle {entry['name']} online",
             "function": partial(webbrowser.open, url)}
        ]
        return actions


class FilterCollections(filter_base.FilterBase):
    def __init__(self, *args, **kwargs):
        super(FilterCollections, self).__init__(*args, **kwargs)
        self.label.setText("Collections")
        self.lineEdit.setPlaceholderText("filter names...")
        self.checkBox.setVisible(False)

    def get_entry_actions(self, row, entry):
        api = get_ckan_api()
        url = f"{api.server}/group/{entry['name']}"
        actions = [
            {"icon": "eye",
             "tooltip": f"view collection {entry['name']} online",
             "function": partial(webbrowser.open, url)}
        ]
        return actions


class FilterDatasets(filter_base.FilterBase):
    def __init__(self, *args, **kwargs):
        super(FilterDatasets, self).__init__(*args, **kwargs)
        self.label.setText("Datasets")
        self.lineEdit.setPlaceholderText("filter titles...")
        self.checkBox.setVisible(False)

    def get_entry_actions(self, row, entry):
        api = get_ckan_api()
        url = f"{api.server}/dataset/{entry['name']}"
        actions = [
            {"icon": "eye",
             "tooltip": f"view dataset {entry['name']} online",
             "function": partial(webbrowser.open, url)}
        ]
        return actions


class FilterResources(filter_base.FilterBase):
    def __init__(self, *args, **kwargs):
        super(FilterResources, self).__init__(*args, **kwargs)
        self.label.setText("Resources")
        self.lineEdit.setPlaceholderText("filter file names...")
        self.checkBox.setVisible(True)
        self.checkBox.setText(".rtdc only")
        self.checkBox.setChecked(True)

    def get_entry_actions(self, row, entry):
        api = get_ckan_api()
        url = f"{api.server}/dataset/{entry['package_id']}/" \
              + f"resource/{entry['id']}"
        actions = [
            {"icon": "eye",
             "tooltip": f"view resource {entry['name']} online",
             "function": partial(webbrowser.open, url)}
        ]
        return actions
