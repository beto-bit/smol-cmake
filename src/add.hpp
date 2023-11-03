#include <concepts>

template <class T>
concept Numeric = std::integral<T> || std::floating_point<T>;


constexpr auto sum() {
    return 0;
}

template <Numeric T, Numeric... Ts>
constexpr auto sum(T first, Ts... args) {
    return first + sum(args...);
}
