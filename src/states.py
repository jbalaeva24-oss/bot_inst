from aiogram.fsm.state import State, StatesGroup


class F(StatesGroup):
    # Блок 1 — вход
    intent = State()

    # Блок 2 — демо
    demo_site_reaction = State()
    demo_bot_reaction = State()

    # Блок 3 — квалификация
    q_leads = State()
    q_budget = State()
    q_timeline = State()

    # Блок 4 — КП
    offer_reaction = State()

    # Блок 5 — возражения
    objection = State()

    # Запись на созвон
    booking_time = State()
    booking_contact = State()
