from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from redforge.roadmap_v140.models import ProviderUsage


class RoutedProvider(Protocol):
    name: str
    model: str

    def generate(self, prompt: str) -> str: ...


@dataclass(slots=True)
class ProviderSlot:
    provider: RoutedProvider
    priority: int = 100
    enabled: bool = True
    max_failures: int = 3
    failures: int = 0


class LLMRouter:
    def __init__(self, *, max_estimated_cost_usd: float = 5.0) -> None:
        self.max_estimated_cost_usd = max_estimated_cost_usd
        self._slots: list[ProviderSlot] = []
        self.usage: list[ProviderUsage] = []

    def register(
        self,
        provider: RoutedProvider,
        *,
        priority: int = 100,
        max_failures: int = 3,
    ) -> None:
        self._slots.append(
            ProviderSlot(
                provider=provider,
                priority=priority,
                enabled=True,
                max_failures=max_failures,
                failures=0,
            )
        )
        self._slots.sort(key=lambda slot: slot.priority)

    def generate(self, prompt: str) -> str:
        if self.total_estimated_cost_usd >= self.max_estimated_cost_usd:
            raise RuntimeError("LLM cost budget exhausted.")

        errors: list[str] = []
        for slot in self._slots:
            if not slot.enabled or slot.failures >= slot.max_failures:
                continue

            started = perf_counter()
            try:
                output = slot.provider.generate(prompt)
                self.usage.append(
                    ProviderUsage(
                        provider=slot.provider.name,
                        model=slot.provider.model,
                        latency_seconds=perf_counter() - started,
                    )
                )
                return output
            except Exception as exc:
                slot.failures += 1
                errors.append(f"{slot.provider.name}: {exc}")

        raise RuntimeError("No LLM provider succeeded: " + "; ".join(errors))

    @property
    def total_estimated_cost_usd(self) -> float:
        return sum(item.estimated_cost_usd for item in self.usage)
