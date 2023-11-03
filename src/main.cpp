#include <array>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>

#include <fmt/core.h>

#include "add.hpp"


constexpr auto sum_all(const std::ranges::range auto& container) {
    return std::accumulate(container.begin(), container.end(), 0);
}

struct Juan{};

int main() {
    constexpr std::array arr{ 1, 2, 3, 4, 5 };
    constexpr int ss = sum(1, 2, 3, 4, 5);

    fmt::println("{}", ss);
}

