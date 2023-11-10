#include <fmt/core.h>

#include <array>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>

#include "bin_search.hpp"

int main() {
    constexpr std::array arr {0, 1, 2, 3, 4, 5};
    constexpr auto index = binary_search(arr, 2);

    fmt::println("Index is {}", index.value_or(69));
}
