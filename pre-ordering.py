import logging
import uuid
# FIX: Added CopyTextButton to the import list
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# BOT TOKEN
BOT_TOKEN = '8669014809:AAGOBc4Hejkz-mF9XrtgayCoL-vJ-lq1ybE'

# YOUR ADMIN GROUP ID
YOUR_CHAT_ID = -1004321898767

# YOUR UPI ID
UPI_ID = "akshatgupta87360@okicici" 

# Menu
MENU = {
    "samosa":   {"name": "Samosa 2pc",    "price": 20},
    "chola":    {"name": "Chola Samosa",  "price": 50},
    "chai":     {"name": "Chai",          "price": 10},
    "paratha":  {"name": "Aloo Paratha",  "price": 45},
    "chips":    {"name": "Chips/Kurkure", "price": 10},
    "drink":    {"name": "Cold Drink",    "price": 10},
    "sandwich": {"name": "Sandwich",      "price": 60},
    "proll":    {"name": "Paneer Roll",   "price": 90},
    "vroll":    {"name": "Veg Roll",      "price": 80},
    "bhature":  {"name": "Chole Bhature", "price": 60},
    "pasta":    {"name": "Pasta",         "price": 60},
}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Temporary_storage for pending orders
pending_orders = {}

def get_cart_summary(cart):
    if not cart:
        return " Your cart is empty."
    receipt = {}
    total_bill = 0
    for item in cart:
        receipt[item['name']] = receipt.get(item['name'], 0) + 1
        total_bill += item['price']
    text = "\n".join([f"• {name} x{qty}" for name, qty in receipt.items()])
    return f" *Current Cart:*\n{text}\n\n💰 *Total: ₹{total_bill}*"

def get_menu_keyboard():
    keyboard = []
    items = list(MENU.items())
    for i in range(0, len(items), 2):
        row = []
        key1, item1 = items[i]
        row.append(InlineKeyboardButton(f"{item1['name']} - ₹{item1['price']}", callback_data=f"add_{key1}"))
        if i + 1 < len(items):
            key2, item2 = items[i+1]
            row.append(InlineKeyboardButton(f"{item2['name']} - ₹{item2['price']}", callback_data=f"add_{key2}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(" Checkout", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton(" Clear Cart", callback_data="clear")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cart'] = []  
    context.user_data['waiting_for_ss'] = False 
    await update.message.reply_text(
        " *Welcome to Samosa Express!*\nTap items to add them to your cart:",
        reply_markup=get_menu_keyboard(),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if 'cart' not in context.user_data:
        context.user_data['cart'] = []

    if query.data.startswith("add_"):
        item_key = query.data.replace("add_", "")
        item = MENU.get(item_key)
        context.user_data['cart'].append(item)
        cart_summary = get_cart_summary(context.user_data['cart'])
        
        await query.edit_message_text(
            f" Added *{item['name']}*!\n\n{cart_summary}\n\nAdd more items or proceed to checkout:",
            reply_markup=get_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif query.data == "clear":
        context.user_data['cart'] = []
        await query.edit_message_text(
            " *Cart Cleared!*\n\nTap items to start again:",
            reply_markup=get_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif query.data == "cancel":
        context.user_data['cart'] = []
        context.user_data['waiting_for_ss'] = False
        await query.edit_message_text(" Your order has been cancelled.\n\nSend /start to order again.")

    elif query.data == "checkout":
        cart = context.user_data['cart']
        if not cart:
            await query.edit_message_text(" Your cart is empty! Add some items first.")
            return

        total_bill = sum(item['price'] for item in cart)
        receipt = {}
        for item in cart:
            receipt[item['name']] = receipt.get(item['name'], 0) + 1
        receipt_text = "\n".join([f"• {name} x{qty}" for name, qty in receipt.items()])

        # Set state to waiting for screenshot
        context.user_data['waiting_for_ss'] = True
        context.user_data['pending_bill'] = total_bill
        context.user_data['pending_receipt'] = receipt_text

        # Using CopyTextButton properly
        keyboard = [
            [InlineKeyboardButton(" Copy UPI ID", copy_text=CopyTextButton(text=UPI_ID))],
            [InlineKeyboardButton(" Cancel Order", callback_data="cancel")]
        ]

        await query.edit_message_text(
            f" *FINAL BILL*\n\n{receipt_text}\n-------------------\n"
            f" *Total: ₹{total_bill}*\n\n"
            f" *HOW TO PAY:*\n"
            f"1... Tap 'Copy UPI ID' and pay *₹{total_bill}* in GPay/PhonePe.\n"
            f"2... Take a screenshot of the success screen (showing Txn ID & Amount).\n"
            f"3... **Send that screenshot here to confirm your order.**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If not checking out...ignore photos
    if not context.user_data.get('waiting_for_ss'):
        return

    if not update.message.photo:
        await update.message.reply_text(" Please send an *image screenshot* of your payment.", parse_mode="Markdown")
        return

    student = update.message.from_user
    student_name = student.full_name or student.username or "Student"
    photo_file_id = update.message.photo[-1].file_id 
    total_bill = context.user_data.get('pending_bill')
    receipt_text = context.user_data.get('pending_receipt')

    # Tell user its sent
    await update.message.reply_text(" *Screenshot received!* Waiting for shopkeeper to verify...", parse_mode="Markdown")

    # Generate short ID for buttons
    order_id = str(uuid.uuid4())[:8] 
    pending_orders[order_id] = {
        "student_id": student.id,
        "total_bill": total_bill,
        "receipt_text": receipt_text
    }
    
    admin_keyboard = [[
        InlineKeyboardButton(" Approve", callback_data=f"approve_{order_id}"),
        InlineKeyboardButton(" Reject", callback_data=f"reject_{order_id}")
    ]]
    
    try:
        # Send structured ticket to Admin Group
        await context.bot.send_photo(
            chat_id=YOUR_CHAT_ID,
            photo=photo_file_id,
            caption=f" *NEW ORDER RECEIVED*\n\n"
                    f" *Student:* {student_name}\n"
                    f" *Username:* @{student.username or 'none'}\n\n"
                    f" *Items:*\n{receipt_text}\n\n"
                    f" *Total to check: ₹{total_bill}*\n\n"
                    f" *Shopkeeper: Verify screenshot matches ₹{total_bill}, then tap Approve.*",
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f" Failed to send to group: {e}")

    # Reset user state so they don't get stuck
    context.user_data['waiting_for_ss'] = False
    context.user_data['cart'] = []

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    action = parts[0]
    order_id = parts[1]

    order = pending_orders.get(order_id)
    if not order:
        await query.edit_message_caption(caption=f"{query.message.caption}\n\n *Order details expired.*", parse_mode="Markdown")
        return

    student_id = order["student_id"]
    total_bill = order["total_bill"]
    receipt_text = order["receipt_text"]

    if action == "approve":
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n *VERIFIED & APPROVED BY SHOPKEEPER*", 
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=student_id,
                text=f" *Order Confirmed!*\n\nYour payment was verified.\n\n *Items:*\n{receipt_text}\n\nShow this receipt at the counter. **Pickup in 5 mins!**",
                parse_mode="Markdown"
            )
        except:
            pass

    elif action == "reject":
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n *REJECTED BY SHOPKEEPER*", 
            parse_mode="Markdown"
        )
        try:
            await context.bot.send_message(
                chat_id=student_id,
                text=" *Order Rejected.*\nThe payment screenshot was invalid or amount was incorrect. Please try again or pay at the counter.",
                parse_mode="Markdown"
            )
        except:
            pass

    pending_orders.pop(order_id, None)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(add_|checkout|cancel|clear)"))
    app.add_handler(CallbackQueryHandler(handle_admin_action, pattern="^(approve_|reject_)")) 
    
    # Handles the screenshot directly
    app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    print(" :) Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()