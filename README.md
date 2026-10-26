Pre-ordering-vai-telegram-bot
A zero-install ordering system for campus food courts, built with Python and the Telegram Bot API. It reduces rush-hour queues by letting students order and pay from their phones, while giving shopkeepers a simple approve/reject dashboard inside Telegram.

~Telegram Food Ordering Bot

> A zero-install, zero-friction ordering system for campus food courts.
> Built with Python + Telegram Bot API to eliminate queues, reduce rush-hour chaos,
> and give shopkeepers a simple approve/reject dashboard — all inside an app students already have.

# The Problem

During peak hours(lunch break), the campus food court faces:

 Long physical queues | Students waste 15–25 minutes standing in line 
Missed classes | Students skip food or rush and miss the first 10 mins of class 
app fatigue Existing food apps (Zomato/Swiggy) are overkill — heavy downloads, delivery fees, no campus-specific menus 
Payment confusion Cash handling + change-making slows the counter
Shopkeeper overload | One person juggles order-taking, cooking, payment, and delivery 
No audit trail | If payment disputes happen, there's no screenshot proof

Students don't want another app. Shopkeepers don't want another dashboard.

The Solution

Telegram bot no app download, no signup, no new UI to learn.

- Students already have Telegram → open bot → tap items → pay via UPI → send screenshot → done.
- Shopkeeper already uses Telegram → receives each order as a photo ticket with Approve/Reject buttons in a private group.
- Zero external app installs for either side. 

Key design wins:
-  No new app to download → adoption friction = ~0
-  UPI copy button → one tap to pay, exact amount pre-filled
-  Screenshot proof → fraud prevention + audit trail
-  One-tap admin approval → shopkeeper stays at the counter, no separate dashboard
-  Async bot → handles **many students simultaneously** during rush


# Google Form Survey (Problem Validation)

Before building, a survey was conducted among campus students to validate the problem.

## Table of Contents
1. The Problem
2. The Solution
3. Google Form Survey
4. User Flow
5. Shopkeeper Flow
6. Python Concepts Used
7. Tech Stack
8. Future roadmap

## This same ordering system can also be built on WhatsApp using the WhatsApp Business API, so students would not even need Telegram. They would just message the shop's WhatsApp number, tap the menu, pay via UPI, and send a screenshot, and the shopkeeper would approve the order in the same chat. The core logic stays exactly the same; only the messaging platform changes. However, WhatsApp requires business verification and approval from Meta before the API can be used, which takes time and documentation, so Telegram was chosen first to launch quickly and validate the idea.

##

```````````````````````````````````````````````````````````````````
1. The Problem
During peak hours (lunch break, roughly 1 PM to 2 PM), the campus food court faces several issues:
Long physical queues. Students waste 15 to 25 minutes standing in line.
Missed classes. Students either skip food or rush and arrive late to class.
App fatigue. Existing food apps such as Zomato or Swiggy are too heavy. They require downloads, charge delivery fees, and do not carry campus-specific menus.
Payment confusion. Cash handling and change-making slow down the counter.
Shopkeeper overload. One person must take orders, cook, handle payment, and manage delivery.
No audit trail. When payment disputes happen, there is no proof of transaction.
Students do not want another app to download. Shopkeepers do not want another dashboard to learn.

2. The Solution
This is a Telegram bot. Students already have Telegram installed. They open the bot, tap items, pay via UPI, send a payment screenshot, and the order is confirmed.
The shopkeeper receives each order as a photo ticket with Approve and Reject buttons in a private Telegram group. No new app is required for either side.

Key design decisions :
*No new app download. Adoption friction is close to zero.
*One-tap UPI copy button. The exact amount is pre-filled, so no manual typing.
*Screenshot proof. Each payment is verified and archived for disputes.
*One-tap approval. The shopkeeper stays at the counter and does not need a separate screen.
*Asynchronous bot. It handles many students at the same time during rush hour.

3. Google Form Survey
Before building, a survey was conducted among campus students to validate the problem,...that Survey file i atteched about in repository
Conclusion: Students want low-friction ordering, not another app. This directly shaped the no-download design decision.

4. User Flow
Student opens the bot ->
/start shows the menu with inline buttons ->
Tap items. Cart updates live. ->
Tap Checkout. Final bill is shown. ->
Tap Copy UPI ID. Paste in GPay or PhonePe. ->
Pay the exact amount. Take a screenshot of the success screen. ->
Send the screenshot in the bot. Bot says "Waiting for verification." ->
Bot confirms: "Order Confirmed. Pickup in 5 minutes...
No app install. No login. No form. About 30 seconds total.


5. Shopkeeper Flow
[Payment Screenshot]
NEW ORDER RECEIVED
Student: xyz
Username: @xyz_
Items:
Samosa 2pc x2
Chai x1

Total to check: Rs 50
[ Approve ]  [ Reject ]

Tap Approve. The student instantly receives "Order Confirmed. Pickup in 5 minutes."
Tap Reject. The student is told to retry or pay at the counter.
The ticket caption updates automatically with a VERIFIED or REJECTED stamp for record keeping.
The shopkeeper stays at the counter. No separate screen, no training required


4. Python Concepts Used
1. python-telegram-bot library
   ...Application, CommandHandler, CallbackQueryHandler
2. Async and await
   ...async def start, await query.edit_message_text
3. Dictionaries
 ...MENU, pending_orders
4. Per-user state
 ...context.user_data with cart and waiting_for_ss
5. Inline Keyboards
...InlineKeyboardMarkup, CopyTextButton
6. UUID order IDs
...uuid.uuid4() with 8-character cut
7. Try and except
...Sending to group, notifying students
8. Logging
...logging.basicConfig
13. String split
..."approve_7b1e4f9a" splits into action and ID
14. Regex routing
...pattern="^(approve_|reject_)"
15. if name == "main"
...Entry point
16. State machine via flags
...waiting_for_ss = True or False
17. F-strings and Markdown
...Bill formatting

5. Tech Stack
Python 3.10 or higher
python-telegram-bot version 21 or higher (async API)
UPI (GPay, PhonePe, Paytm) for payments
Google Forms for pre-build user research
No database required. Orders are stored in a pending_orders dictionary. This can be upgraded to SQLite or Redis later.

6. Future Roadmap
Move secrets to .env (security improvement)
Add SQLite persistence so orders survive bot restart
Live order status. Notify student when order is preparing and when ready for pickup.
Order history command. /myorders
Multi-shop support. One bot, many counters.
Auto UPI verification via Razorpay or UPI webhook. Removes manual approve step.
Dynamic UPI QR code instead of copy-paste
Analytics. Daily revenue, top items, rush-hour heatmap.
Rate limiting to prevent spam orders

7. Author
Akshat Gupta

Built to solve a real problem on campus: long lunch queues.
Email: akshatgupta87360@gmail.com


**Why Telegram and Not an App**
Because 94% of students already have Telegram installed. The fastest way to kill a queue is to remove the last barrier, which is the app download. That single design choice is the core thesis of this project.
