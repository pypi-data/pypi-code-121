import sys

from html_matcher.export import ExcelExporter
from html_matcher.ms import MatchingSubsequences, MatchingSubsequencesOptimized
from html_matcher.similarity import MixedSimilarity
from html_matcher.style import StyleSimilarity
from html_matcher.ted import AllPathTreeEditDistance, AllPathTreeEditDistanceOptimized
from html_matcher.utils import get_files, get_results

if __name__ == '__main__':
    arguments = sys.argv[1:]
    website = arguments[0]
    path = arguments[1]
    k = float(arguments[2])
    files = get_files(path)

    style = StyleSimilarity()

    ms = MatchingSubsequences()
    final_data, details, duration = get_results(files, ms.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, 'MS', website, len(files))
    exporter.results_to_excel()

    ms_optimized = MatchingSubsequencesOptimized()
    final_data, details, duration = get_results(files, ms_optimized.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, 'X_MS', website, len(files))
    exporter.results_to_excel()

    mixed_ms = MixedSimilarity(ms, style, k)
    final_data, details, duration = get_results(files, mixed_ms.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, f'MS_Style_{int(k * 10)}', website, len(files))
    exporter.results_to_excel()

    mixed_ms_optimized = MixedSimilarity(ms_optimized, style, k)
    final_data, details, duration = get_results(files, mixed_ms_optimized.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, f'X_MS_style_{int(k * 10)}', website, len(files))
    exporter.results_to_excel()

    apted = AllPathTreeEditDistance()
    final_data, details, duration = get_results(files, apted.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, 'APTED', website, len(files))
    exporter.results_to_excel()

    apted_optimized = AllPathTreeEditDistanceOptimized()
    final_data, details, duration = get_results(files, apted_optimized.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, 'X_APTED', website, len(files))
    exporter.results_to_excel()

    mixed_apted = MixedSimilarity(apted, style, k)
    final_data, details, duration = get_results(files, mixed_apted.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, f'APTED_Style_{int(k * 10)}', website, len(files))
    exporter.results_to_excel()

    mixed_apted_optimized = MixedSimilarity(apted_optimized, style, k)
    final_data, details, duration = get_results(files, mixed_apted_optimized.similarity)
    exporter = ExcelExporter(final_data, details, duration, 0, 0.05, f'X_APTED_Style_{int(k * 10)}', website,
                             len(files))
    exporter.results_to_excel()
