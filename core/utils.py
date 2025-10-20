def format_large_number(number: int) -> str:
    """
    格式化大数字，例如将 1234567 格式化为 1.2M。
    """
    if number > 1_000_000_000:
        return f"{round(number / 1_000_000_000, 1)}G"
    elif number > 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    elif number > 1_000:
        return f"{round(number / 1_000, 1)}K"
    else:
        return str(number)
