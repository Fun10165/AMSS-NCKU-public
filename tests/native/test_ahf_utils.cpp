#include <cmath>
#include <iostream>

#include "util.h"

using AHFinderDirect::jtutil::fuzzy;
using AHFinderDirect::jtutil::norm;

int main() {
  if (AHFinderDirect::jtutil::round<double>::to_integer(3.6) != 4) return 1;
  if (AHFinderDirect::jtutil::round<double>::to_integer(-3.6) != -4) return 2;
  if (AHFinderDirect::jtutil::round<double>::floor(-3.1) != -4) return 3;
  if (AHFinderDirect::jtutil::round<double>::ceiling(-3.1) != -3) return 4;

  norm<double> stats;
  stats.data(-2.0);
  stats.data(1.0);
  stats.data(3.0);

  if (std::fabs(stats.mean() - (2.0 / 3.0)) > 1.0e-12) return 5;
  if (std::fabs(stats.two_norm() - std::sqrt(14.0)) > 1.0e-12) return 6;
  if (std::fabs(stats.rms_norm() - std::sqrt(14.0 / 3.0)) > 1.0e-12) return 7;
  if (stats.max_value() != 3.0 || stats.min_value() != -2.0) return 8;

  fuzzy<double>::set_tolerance(1.0e-9);
  if (!fuzzy<double>::EQ(1.0, 1.0 + 5.0e-10)) return 9;
  if (fuzzy<double>::EQ(1.0, 1.0 + 1.0e-6)) return 10;
  if (fuzzy<double>::floor(2.0 + 1.0e-12) != 2) return 11;
  if (fuzzy<double>::ceiling(2.0 - 1.0e-12) != 2) return 12;

  std::cout << "C++ native tests passed" << std::endl;
  return 0;
}
