#include <concepts>

template <class T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <Numeric T>
constexpr auto sum_two(T first, T second) {
    return first + second;
}
