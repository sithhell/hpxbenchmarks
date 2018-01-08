
#include <benchmark/benchmark.h>

class null_reporter : public benchmark::BenchmarkReporter {
  virtual bool ReportContext(const Context& context)
  {
      return true;
  }

  void ReportRuns(const std::vector<Run>& report)
  {
  }
};
