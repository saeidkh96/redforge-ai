from redforge.roadmap_v140 import LLMRouter


class BrokenProvider:
    name = "broken"
    model = "broken-model"

    def generate(self, prompt: str) -> str:
        raise RuntimeError("unavailable")


class WorkingProvider:
    name = "working"
    model = "working-model"

    def generate(self, prompt: str) -> str:
        return f"ok:{prompt}"


def test_router_falls_back_to_next_provider() -> None:
    router = LLMRouter()
    router.register(BrokenProvider(), priority=1)
    router.register(WorkingProvider(), priority=2)
    assert router.generate("hello") == "ok:hello"
    assert router.usage[0].provider == "working"
