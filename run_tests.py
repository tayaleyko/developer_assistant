from __future__ import annotations

import argparse
import sys
import time
import unittest
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Импорт helpers настраивает sys.path для app/
import tests.helpers  # noqa: F401


COMPONENT_NAMES = {
    "test_encoder": "SurveyEncoder",
    "test_app_state": "AppState",
    "test_loader": "loader",
    "test_stack_info": "stack_info",
    "test_ai_stub": "ai_stub",
    "test_mlp_model": "mlp_model",
    "test_site_analyzer": "site_analyzer",
    "test_storage": "storage",
    "test_template_generator": "template_generator",
}


@dataclass
class ComponentStats:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    details: list[tuple[str, str, str | None]] = field(default_factory=list)


class SummaryTestResult(unittest.TestResult):
    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.stats_by_module: dict[str, ComponentStats] = defaultdict(ComponentStats)
        self._current_module = "unknown"
        self._current_test = ""

    def startTest(self, test):
        super().startTest(test)
        module = test.__class__.__module__.split(".")[-1]
        self._current_module = module
        self._current_test = test._testMethodName
        self.stats_by_module[module].total += 1

    def addSuccess(self, test):
        super().addSuccess(test)
        mod = test.__class__.__module__.split(".")[-1]
        st = self.stats_by_module[mod]
        st.passed += 1
        st.details.append((test._testMethodName, "OK", None))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        mod = test.__class__.__module__.split(".")[-1]
        st = self.stats_by_module[mod]
        st.failed += 1
        st.details.append((test._testMethodName, "FAIL", self._format_err(err)))

    def addError(self, test, err):
        super().addError(test, err)
        mod = test.__class__.__module__.split(".")[-1]
        st = self.stats_by_module[mod]
        st.errors += 1
        st.details.append((test._testMethodName, "ERROR", self._format_err(err)))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        mod = test.__class__.__module__.split(".")[-1]
        st = self.stats_by_module[mod]
        st.skipped += 1
        st.details.append((test._testMethodName, "SKIP", reason))

    @staticmethod
    def _format_err(err) -> str:
        if not err:
            return "unknown error"
        if err[1]:
            return str(err[1]).strip().splitlines()[-1]
        return str(err[0])


def discover_tests() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    return loader.discover(start_dir=str(ROOT / "tests"), pattern="test_*.py")


def print_summary(result: SummaryTestResult, elapsed: float, verbose: bool):
    width = 78
    header = f"  {'Компонент':<22} {'Всего':>5}  {'OK':>5}  {'Fail':>4}  {'Err':>3}  {'Skip':>4}"
    print(header)

    totals = ComponentStats()
    for module in sorted(result.stats_by_module):
        st = result.stats_by_module[module]
        name = COMPONENT_NAMES.get(module, module)
        totals.total += st.total
        totals.passed += st.passed
        totals.failed += st.failed
        totals.errors += st.errors
        totals.skipped += st.skipped
        print(
            f"  {name:<22} {st.total:>5}  {st.passed:>5}  {st.failed:>4}  "
            f"{st.errors:>3}  {st.skipped:>4}"
        )
    print(f"\n  Время : {elapsed:.2f} с")

    if verbose:
        print("\n  Детализация:")
        for module in sorted(result.stats_by_module):
            name = COMPONENT_NAMES.get(module, module)
            print(f"\n  [{name}]")
            for test_name, status, info in result.stats_by_module[module].details:
                line = f"    • {test_name}: {status}"
                if info and status != "OK":
                    line += f" — {info}"
                print(line)
    print()
    print(
        f"  {'Итог':<22} {totals.total:>5}  {totals.passed:>5}  {totals.failed:>4}  "
        f"{totals.errors:>3}  {totals.skipped:>4}"
    )


    if result.wasSuccessful():
        print("  Все тесты пройдены!")
    else:
        print(f"  Сбой при выполнении: ошибок: {len(result.errors)}, провалов: {len(result.failures)}")



def main():
    parser = argparse.ArgumentParser(description="Модульные тесты ИС «Ассистент разработчика»")
    parser.add_argument("-v", "--verbose", action="store_true", help="Подробный вывод по каждому тесту")
    args = parser.parse_args()

    suite = discover_tests()
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1, resultclass=SummaryTestResult)
    start = time.perf_counter()
    result = runner.run(suite)
    elapsed = time.perf_counter() - start
    print_summary(result, elapsed, verbose=args.verbose)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
