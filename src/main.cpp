#include <array>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>

#include <fmt/core.h>

#include "add.hpp"
#include "bin_search.hpp"


constexpr auto sum_all(const std::ranges::range auto& container) {
    return std::accumulate(container.begin(), container.end(), 0);
}

struct Juan{};

int main() {
    constexpr std::array arr{0, 1, 2, 3, 4, 5 };

    constexpr auto index = binary_search(arr, 2);

    fmt::println("Index is {}", index.value_or(-1));
}

