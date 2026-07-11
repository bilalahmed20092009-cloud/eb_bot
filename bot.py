numbers_text = '\n'.join([f"- {n}" for n in SETTINGS["PAYMENT_NUMBERS"]])
        text = f"🎁 بيانات إتصالات\n💵 سعر الرقم: {SETTINGS['PRICE']} جنيه\nحول على:\n{numbers_text}"
        keyboard = [[InlineKeyboardButton("تأكيد واختيار العدد", callback_data='choose_count')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'choose_count':
        text = "💳 حدد عدد الأرقام من 1 إلى 10"
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f'count_{i}') for i in range(1,6)],
                    [InlineKeyboardButton(str(i), callback_data=f'count_{i}') for i in range(6,11)]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('count_'):
        count = int(query.data.split('_')[1])
        total = count * SETTINGS["PRICE"]
        user_data[user_id]["count"] = count
        user_data[user_id]["total"] = total
        user_data[user_id]["step"] = "waiting_screenshot"
        numbers_text = '\n'.join([f"- {n}" for n in SETTINGS["PAYMENT_NUMBERS"]])
        text = f"🧾 الاجمالي: {total} جنيه\nحول على:\n{numbers_text}\n\nابعت السكرين"
        await query.edit_message_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text if update.message.text else ""

    if is_admin(user_id) and user_id in user_data:
        step = user_data[user_id].get("step")
        if step == "waiting_new_admin":
            SETTINGS["ADMINS"].append(int(text)); save_settings()
            await update.message.reply_text(f"✅ تم اضافة المشرف {text}")
            user_data.pop(user_id); return
        elif step == "waiting_new_price":
            SETTINGS["PRICE"] = int(text); save_settings()
            await update.message.reply_text(f"✅ تم تغيير السعر")
            user_data.pop(user_id); return
        elif step == "waiting_new_number":
            SETTINGS["PAYMENT_NUMBERS"].append(text); save_settings()
            await update.message.reply_text(f"✅ تم اضافة الرقم")
            user_data.pop(user_id); return

    if user_id in user_data:
        data = user_data[user_id]
        if data.get("step") == "waiting_screenshot" and update.message.photo:
            data["screenshot_id"] = update.message.photo[-1].file_id
            data["step"] = "waiting_sender_number"
            await update.message.reply_text("⭐ استلمنا السكرين!\nابعت الرقم اللي حولت منه:")
        elif data.get("step") == "waiting_sender_number" and text:
            data["sender_number"] = text
            data["step"] = "waiting_target_number"
            await update.message.reply_text("ابعت الرقم اللي عايز بياناته:")
        elif data.get("step") == "waiting_target_number" and text:
            data["target_number"] = text
            await update.message.reply_text("⭐ تم ارسال طلبك للمشرفين!")
            caption = f"🔔 طلب جديد!\nالاسم: {data['name']}\nالعدد: {data['count']}\nالمبلغ: {data['total']}"
            await context.bot.send_photo(chat_id=SETTINGS["ADMINS"][0], photo=data["screenshot_id"], caption=caption)
            user_data.pop(user_id)

app = ApplicationBuilder().token(SETTINGS["TOKEN"]).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))
print("البوت شغال 24/7..."); app.run_polling()
