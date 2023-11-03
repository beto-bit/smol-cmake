#include <array>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>

#include "add.hpp"


constexpr auto sum_all(const std::ranges::range auto& container) {
    return std::accumulate(container.begin(), container.end(), 0);
}


int main() {
    constexpr std::array arr{ 1, 2, 3, 4, 5 };
    constexpr int sum = sum_all(arr);

    std::cout << sum << std::endl;
}

