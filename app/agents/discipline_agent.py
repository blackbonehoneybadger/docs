"""Discipline Agent: direct, no humiliation, eyes on the 2030 goal."""

from app.services.cfo_service import CfoSummary


class DisciplineAgent:
    name = "discipline"

    def render_discipline(self, s: CfoSummary) -> str:
        spend_cap = s.personal_spending_allowance
        lines = [
            "11. Дисциплина",
            "",
            "Сегодня нельзя:",
            f"- тратить больше ${spend_cap:,.2f}",
            "- покупать импульсивно",
            "- лезть all-in",
            "- игнорировать upcoming payments",
            "",
            "Главное действие дня:",
        ]
        if s.upcoming_obligations_total > s.available_cash:
            lines.append("Закрыть кассовый разрыв: обязательства больше доступного cash.")
        elif s.survival_ratio < 1:
            lines.append("Усилить emergency fund — он меньше 1 месяца расходов.")
        elif s.today_free_cash <= 0:
            lines.append("Не тратить. Сохранить cashflow до следующего дохода.")
        else:
            lines.append(
                "Держать план: расходы под контролем, свободные деньги — по плану инвестиций."
            )
        lines += [
            "",
            f"Помни цель 2030: Freedom Ratio сейчас {s.freedom_ratio * 100:.1f}%. "
            "Каждый сохранённый доллар приближает выход из крысиных бегов.",
        ]
        return "\n".join(lines)
