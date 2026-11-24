import random
import time

from app.metrics import edit_magnitude


def test_5000_character_text_pair_under_200ms(record_property):
    rng = random.Random(2074)
    alphabet = "春夏秋冬风雨山海星月光影音乐书信远方"
    draft_chars = [rng.choice(alphabet) for _ in range(5000)]
    final_chars = draft_chars.copy()
    for index in rng.sample(range(5000), 750):
        final_chars[index] = rng.choice(alphabet)
    draft = "".join(draft_chars)
    final = "".join(final_chars)

    elapsed_values = []
    for _ in range(5):
        started = time.perf_counter()
        metrics = edit_magnitude(draft, final, "text")
        elapsed_values.append(time.perf_counter() - started)
    maximum = max(elapsed_values)
    record_property("max_seconds", f"{maximum:.6f}")
    print(f"5000 字对 5000 字：5 次计算最大耗时 {maximum:.6f} 秒")
    assert 0.10 <= metrics.edit_ratio <= 0.20
    assert maximum <= 0.2
