from fusion.signal_engine import SignalEngine


def test_signal_confirm_and_cooldown():
    engine = SignalEngine(confirm_n=2, cooldown_n=1)

    # first signal insufficient confirms
    assert engine.generate(1.0, 0.5) == "NEUTRAL"
    # second confirm triggers LONG
    assert engine.generate(1.0, 0.5) == "LONG"
    # immediate opposite should respect cooldown
    assert engine.generate(-1.0, 0.5) == "LONG"
    # after cooldown next confirm flips
    assert engine.generate(-1.0, 0.5) == "SHORT"


def test_signal_neutral_resets_buffer():
    engine = SignalEngine(confirm_n=2, cooldown_n=1)
    engine.generate(1.0, 0.5)
    assert engine.generate(0.1, 0.5) == "NEUTRAL"
    assert engine.buffer == []
