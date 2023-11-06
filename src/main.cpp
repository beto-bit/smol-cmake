#include <fmt/core.h>

#include <array>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>

#include "add.hpp"
#include "bin_search.hpp"

constexpr auto sum_all(const std::ranges::range auto& container) {
    return std::accumulate(container.begin(), container.end(), 0);
}

template<std::size_t N>
consteval void test_bin_search() {
    constexpr std::array arr {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

    constexpr auto index = binary_search(arr, static_cast<int>(N)).value();
    static_assert(index == N, "God why");
}

consteval void test_all_bin_search() {
    test_bin_search<1>();
    test_bin_search<2>();
    test_bin_search<3>();
    test_bin_search<4>();
    test_bin_search<5>();
    test_bin_search<6>();
    test_bin_search<7>();
    test_bin_search<8>();
    test_bin_search<9>();
}

int main() {
    test_all_bin_search();

    constexpr std::array arr {0, 1, 2, 3, 4, 5};
    constexpr auto index = binary_search(arr, 69);

    fmt::println("Index is {}", index.value_or(69));
}
