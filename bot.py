async def handle_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    subject = query.data
    folder_id = folders.get(subject)
    if not folder_id:
        await query.edit_message_text("لا يوجد مجلد مخصص لهذا التخصص.")
        return

    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, webViewLink)"
    ).execute()
    files = results.get('files', [])

    if not files:
        await query.edit_message_text(f"لا توجد محاضرات مرفوعة لتخصص {subjects[subject]}.")
        return

    keyboard = [[InlineKeyboardButton(file['name'], url=file['webViewLink'])] for file in files]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"محاضرات تخصص {subjects[subject]}:", reply_markup=reply_markup)
