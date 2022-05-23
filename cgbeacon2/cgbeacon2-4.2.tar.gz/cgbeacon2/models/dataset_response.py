# -*- coding: utf-8 -*-


class DatasetAlleleResponse:
    """Create a Beacon Dataset Allele Response object to be returned by Beacon Response"""

    def __init__(self, dataset, variants) -> None:
        self.datasetId = dataset["_id"]
        n_samples, n_alleles, n_variants = self._sample_allele_variant_count(
            self.datasetId, variants
        )
        self.sampleCount = n_samples
        self.callCount = n_alleles
        self.variantCount = n_variants
        self.info = self._info(dataset)
        self.exists = True if self.sampleCount > 0 else False

    def _info(self, dataset) -> dict:
        """Provides additional info regarding a dataset object

        Accepts:
            dataset(dict)

        Returns:
            info(dict)
        """
        info = dict(accessType=dataset["authlevel"].upper())
        return info

    def _sample_allele_variant_count(self, dataset_id, variants) -> tuple:
        """Counts samples and allelic calls for one or more variants

        Accepts:
            dataset_id(str)
            variants(list)

        Returns:
            n_samples(int), n_calls(int)
        """
        n_samples = 0
        n_calls = 0
        n_variants = 0
        for variant_obj in variants:
            if dataset_id in variant_obj.get("datasetIds"):
                if variant_obj["datasetIds"][dataset_id].get("samples"):
                    n_samples += len(variant_obj["datasetIds"][dataset_id]["samples"].keys())
                n_variants += 1
                n_calls += variant_obj["call_count"]
        return n_samples, n_calls, n_variants
