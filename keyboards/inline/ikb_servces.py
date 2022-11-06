from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_payment_services = InlineKeyboardMarkup(row_width=2)
inline_payment_bankcard_button = InlineKeyboardButton("Картой💳", url="https://kaspi.kz")
inline_payment_cash = InlineKeyboardButton("В барбершопе 🏢", callback_data="cashpayment")
inline_payment_services.add(inline_payment_bankcard_button, inline_payment_cash)
