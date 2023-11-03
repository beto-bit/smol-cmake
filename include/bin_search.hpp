#include <concepts>
#include <compare>
#include <cstddef>
#include <iterator>
#include <optional>

template <class Cont, class T>
concept Container = requires (Cont con, T val) {
    { con.begin() } -> std::random_access_iterator;
    { con.end() } -> std::random_access_iterator;
    { con.size() } -> std::same_as<std::size_t>;
    { typename Cont::value_type() } -> std::same_as<T>;
};


template <std::three_way_comparable Item>
[[nodiscard]]
constexpr std::optional<std::size_t> binary_search(
    const Container<Item> auto& container,
    const Item& target,
    std::size_t left,
    std::size_t right
) noexcept
{
    const auto access = container.begin();

    if (left > right)
        return std::nullopt;

    std::size_t middle = left + (right - left) / 2;

    if (access[middle] == target)
        return middle;
    
    if (access[middle] < target)
        return binary_search(container, target, middle + 1, right);
    else
        return binary_search(container, target, left, middle - 1);
}


template <std::three_way_comparable Item>
[[nodiscard]]
constexpr std::optional<std::size_t> binary_search(
    const Container<Item> auto& container,
    const Item& target
) noexcept
{
    return binary_search(
        container,
        target,
        0,
        container.size()
    );
}