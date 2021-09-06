from functools import lru_cache


class DBExtract:
    def __init__(self, datasets):
        """User-convenient access to dataset search results

        Parameters
        ----------
        datasets: list
            List of CKAN package dictionaries
        """
        self._circles = None
        self._collections = None
        self._dataset_name_index = None

        self.registry = {}
        self.datasets = []
        self._add_datasets(datasets)

    def __add__(self, other):
        return DBExtract(self.datasets + other.datasets)

    def __iadd__(self, other):
        self._add_datasets(other.datasets)
        return self

    def __len__(self):
        return len(self.datasets)

    def __iter__(self):
        return iter(self.datasets)

    def _add_datasets(self, datasets):
        for dd in datasets:
            name = dd["name"]
            if name not in self.registry:  # datasets must only be added once
                self.registry[name] = dd
                self.datasets.append(dd)

    @property
    @lru_cache(maxsize=1)
    def circles(self):
        if not self._circles:
            circ_list = []
            circ_names = []
            for dd in self.datasets:
                name = dd["organization"]["name"]
                if name not in circ_names:
                    circ_list.append(dd["organization"])
                    circ_names.append(name)
            self._circles = sorted(
                circ_list, key=lambda x: x.get("title") or x["name"])
        return self._circles

    @property
    @lru_cache(maxsize=1)
    def collections(self):
        if not self._collections:
            coll_list = []
            coll_names = []
            for dd in self.datasets:
                for gg in dd["groups"]:
                    name = gg["name"]
                    if name not in coll_names:
                        coll_list.append(gg)
                        coll_names.append(name)
            self._collections = sorted(
                coll_list, key=lambda x: x.get("title") or x["name"])
        return self._collections

    def get_dataset_dict(self, dataset_name):
        return self.registry[dataset_name]
